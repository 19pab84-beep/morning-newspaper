"""Optional live original AI writing using Responses API with strict JSON.

No RSS fallback, no fabricated sources, no secret lore in prompts or logs.
Live mode must be explicitly selected and configured with a model and key.
"""
from __future__ import annotations
import copy
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

TEXT_SCHEMA={
 'type':'object','additionalProperties':False,
 'properties':{
  'headline':{'type':'string'}, 'deck':{'type':'string'},
  'paragraphs':{'type':'array','items':{'type':'string'}},
  'specifics':{'type':'array','items':{'type':'string'}},
  'claims':{'type':'array','items':{'type':'object','additionalProperties':False,
   'properties':{'text':{'type':'string'},'source_id':{'type':'string'},'evidence_id':{'type':'string'}},
   'required':['text','source_id','evidence_id']}}},
 'required':['headline','deck','paragraphs','specifics','claims']}
REVIEW_SCHEMA={'type':'object','additionalProperties':False,
 'properties':{'approved':{'type':'boolean'},'issues':{'type':'array','items':{'type':'string'}}},
 'required':['approved','issues']}


class Response:
    def __init__(self, status, data):
        self.status_code=status
        self.data=data

    def json(self):
        return json.loads(self.data)


class Session:
    def post(self, url, *, json, headers, timeout):
        request=Request(url,data=__import__('json').dumps(json).encode(),
                        headers={**headers,'Content-Type':'application/json'},method='POST')
        try:
            with urlopen(request,timeout=timeout[1]) as response:
                return Response(response.status,response.read())
        except HTTPError as error:
            return Response(error.code,b'{}')


def validate_shape(value,schema):
    """Validate the restricted object/array/string/bool contracts used here.

    This is deliberately not advertised as a general JSON Schema engine.
    Unknown schema constructs fail closed instead of being silently ignored.
    """
    if set(schema)-{'type','properties','required','additionalProperties','items'}:
        raise ValueError('Unsupported contract construct')
    kind=schema['type']
    if kind=='object':
        if not isinstance(value,dict):
            raise ValueError('Expected object')
        props=schema['properties']
        if not set(schema['required']).issubset(value) or set(value)-set(props):
            raise ValueError('Missing or extra fields')
        for key,item in value.items():
            validate_shape(item,props[key])
    elif kind=='array':
        if not isinstance(value,list):
            raise ValueError('Expected array')
        for item in value:
            validate_shape(item,schema['items'])
    elif kind=='string':
        if not isinstance(value,str):
            raise ValueError('Expected string')
    elif kind=='boolean':
        if type(value) is not bool:
            raise ValueError('Expected bool')
    else:
        raise ValueError('Unsupported type')


class ResponsesAuthor:
    def __init__(self,model,*,max_calls=16,max_output_tokens=6000,session=None):
        self.key=os.environ.get('OPENAI_API_KEY')
        if not self.key or not model:
            raise RuntimeError('Tryb live wymaga OPENAI_API_KEY oraz jawnego --model; brak zastępczego tekstu')
        self.model=model
        self.max_calls=max_calls
        self.max_output_tokens=max_output_tokens
        self.calls=0
        self.usage={'input_tokens':0,'output_tokens':0}
        self.session=session or Session()

    def ask(self,role,instruction,payload,schema):
        if self.calls>=self.max_calls:
            raise RuntimeError('Limit wywołań AI na numer')
        self.calls+=1
        body={'model':self.model,'store':False,'max_output_tokens':self.max_output_tokens,
              'input':[{'role':'system','content':instruction},
                       {'role':'user','content':json.dumps(payload,ensure_ascii=False)}],
              'text':{'format':{'type':'json_schema','name':role,'strict':True,'schema':schema}}}
        try:
            r=self.session.post('https://api.openai.com/v1/responses',json=body,
                headers={'Authorization':'Bearer '+self.key},timeout=(10,180))
        except (OSError,URLError):
            raise RuntimeError('API niedostępne; numer nie został wydany') from None
        if r.status_code!=200:
            raise RuntimeError('AI HTTP '+str(r.status_code)+'; treść odpowiedzi nie jest logowana')
        data=r.json()
        if data.get('status')!='completed':
            raise RuntimeError('AI nie zakończyło odpowiedzi; brak publikacji')
        parts=[c for o in data.get('output',[]) for c in o.get('content',[])]
        if any(c.get('type')=='refusal' for c in parts):
            raise RuntimeError('AI odmówiło; brak automatycznego zastępowania tekstu')
        text=''.join(c.get('text','') for c in parts if c.get('type')=='output_text')
        try:
            result=json.loads(text)
            validate_shape(result,schema)
        except Exception:
            raise RuntimeError('Niepoprawny wynik strukturalny AI') from None
        for k in self.usage:
            self.usage[k]+=data.get('usage',{}).get(k,0)
        return result

    def rewrite(self,issue,public_context):
        result=copy.deepcopy(issue)
        for story in result['stories']:
            payload={'assignment':{k:story[k] for k in ('story_id','role','type','topic','rubric')},
                     'outline':story.get('brief') or story['paragraphs'], 'source_packets':result['sources'],
                     'safe_canon_context':public_context,
                     'required_public_claims':story.get('canon_claims',[]),
                     'required_clue_carriers':[c for c in public_context['clues'] if c['carrier']==story['story_id']],
                     'target_words':story.get('target_words') or len(' '.join(story['paragraphs']).split())
                                    or {'cover':320,'feature':480,'short':140}[story['role']]}
            generated=self.ask('writer',
                'Napisz autorski polski tekst do starej gazety. Jedna konkretna teza, bez pustych sloganów. '
                'Materiały sourced_feature: wszystkie fakty tylko z pakietów źródłowych; minimum 3 konkrety. '
                'Fikcja: poważny lokalny reportaż; zachowaj dosłowne publiczne fakty i przydzielone tropy. '
                'Nie dodawaj nowych tajemnic, faktów kanonu ani cytatów prawdziwych osób. '
                'Opinia i propozycje ćwiczeń muszą być rozpoznawalne. Nie wpisuj daty, numeru ani odsyłaczy str. N. '
                'Długość bliska target_words, tolerancja 5%. Zero markup.',payload,TEXT_SCHEMA)
            story.update(generated)
        review=self.ask('copy_editor',
            'Oceń kompletny numer pod względem źródeł, konkretów, polszczyzny, spójności scen '
            'i poprawności fabularnych faktów. Nie wolno aprobować sprzeczności ani dowodów spoza source_packets. '
            'Zwróć approved=false, jeśli potrzebna jest poprawka.',
            {'issue':result,'safe_canon_context':public_context},REVIEW_SCHEMA)
        if not review['approved'] or review['issues']:
            raise ValueError('Kontroler AI odrzucił numer: '+'; '.join(review['issues']))
        result['provenance']={'author':'OpenAI Responses API','model':self.model,
                              'api_calls':self.calls,'usage':self.usage}
        result['editorial_review']={'status':'APPROVED_FOR_PILOT','reviewer':'API copy_editor',
                                    'limitations':'Ocena modelu wymaga ludzkiej akceptacji pilota'}
        return result
