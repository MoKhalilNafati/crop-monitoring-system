from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import AnomalyEvent, AgentRecommendation
from .rules import RuleEngine

@receiver(post_save, sender=AnomalyEvent)
def trigger_agent_analysis(sender, instance, created, **kwargs):
    """
    Listens for new AnomalyEvents.
    When one is created, it runs the Rule Engine and saves a Recommendation.
    [cite_start]Source: Project Doc [cite: 69-71]
    """
    if created:
        print(f"⚡ SIGNAL RECEIVED: Anomaly {instance.id} created. Waking Agent...")
        
        try:
            # 1. Initialize the Brain
            engine = RuleEngine()
            
            # 2. Ask for advice (This now uses the updated RuleEngine logic)
            analysis = engine.analyze(instance)
            
            # 3. Save the Recommendation to DB
            AgentRecommendation.objects.create(
                anomaly_event=instance,
                recommended_action=analysis['action'],
                explanation_text=analysis['explanation'],
                confidence=analysis['confidence']
            )
            print(f"🤖 AGENT: Recommendation saved for Anomaly {instance.id}")

        except Exception as e:
            # Safety net: If the Agent crashes, print the error but don't kill the server
            print(f"❌ AGENT ERROR: Failed to generate recommendation: {e}")