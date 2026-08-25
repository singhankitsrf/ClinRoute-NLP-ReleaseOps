from clinroute.service import NLPService
class MockPredictor:
    version="mock-v1"
    def predict(self,text): return {"route":"otology","route_confidence":0.91,"urgency":"routine","urgency_confidence":0.88}
def test_service_composes_prediction_redaction_and_entities():
    result=NLPService(MockPredictor()).analyze("Ear pain for 2 weeks. Email demo.person@example.test. MRN SYN-123456."); assert result["route"]=="otology"; assert result["review_required"] is False; assert "[EMAIL_REDACTED]" in result["redacted_text"]; assert result["model_version"]=="mock-v1"; assert any(e["type"]=="SYMPTOM" for e in result["entities"])
