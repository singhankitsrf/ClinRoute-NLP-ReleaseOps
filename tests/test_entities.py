from clinroute.entities import extract_entities
def test_extracts_symptom_and_duration():
    entities=extract_entities("Persistent ear pain for 2 weeks with tinnitus."); assert any(e.type=="SYMPTOM" and "ear pain" in e.value.lower() for e in entities); assert any(e.type=="DURATION" for e in entities)
