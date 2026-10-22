from app.services.learning_journey import LearningJourneyService

service = LearningJourneyService()

# Test 1: High score
assessment = {
    "score": 100,
    "feedback": [],
}

result = service.recommend_next_step(assessment)

print("Test 1: High Score")
print(result)

assert result["recommendation"] == "ADVANCE"
assert result["next_step"] == "WIFI-002"


# Test 2: Medium score
assessment = {
    "score": 60,
    "feedback": [
        "Did not verify Wi-Fi status after remediation."
    ],
}

result = service.recommend_next_step(assessment)

print("\nTest 2: Medium Score")
print(result)

assert result["recommendation"] == "PRACTICE"
assert result["next_step"] == "RETRY_CURRENT_SCENARIO"


# Test 3: Low score
assessment = {
    "score": 30,
    "feedback": [
        "Did not check Wi-Fi status.",
        "Did not complete the simulated remediation.",
    ],
}

result = service.recommend_next_step(assessment)

print("\nTest 3: Low Score")
print(result)

assert result["recommendation"] == "REVIEW"
assert result["next_step"] == "REVIEW_KNOWLEDGE_AND_RETRY"


print("\nAll Learning Journey tests passed!")