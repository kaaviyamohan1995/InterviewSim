import random


QUESTION_TYPES = {
    1: [
        "resume_deep_dive",
        "technical_concept"
    ],

    2: [
        "scenario_debugging",
        "problem_solving",
        "technical_concept"
    ],

    3: [
        "tradeoff_analysis",
        "real_world_application",
        "scenario_debugging"
    ]
}


def choose_difficulty(
    round_num,
    step
):

    if round_num == 1:
        return "easy"

    elif round_num == 2:

        if step <= 2:
            return "medium"

        return "hard"

    return "hard"


def select_question_type(
    round_num,
    previous_types
):

    candidates = QUESTION_TYPES.get(
        round_num,
        QUESTION_TYPES[2]
    )

    available = [
        q for q in candidates
        if q not in previous_types[-2:]
    ]

    if not available:
        available = candidates

    return random.choice(available)


def score_topics(
    concept_map,
    job_description,
    asked_topics,
    round_num
):

    topic_scores = {}

    jd_lower = (
        job_description or ""
    ).lower()

    for topic, subtopics in concept_map.items():

        score = 1

        # ----------------------
        # JD ALIGNMENT
        # ----------------------
        if topic.lower() in jd_lower:
            score += 5

        for sub in subtopics:

            if sub.lower() in jd_lower:
                score += 2

        # ----------------------
        # REPETITION PENALTY
        # ----------------------
        asked_count = asked_topics.count(topic)

        score -= asked_count * 2

        # ----------------------
        # ROUND STRATEGY
        # ----------------------
        if round_num == 1:
            # broad fundamentals first
            score += 2

        elif round_num == 2:
            # technical depth
            score += 3

        elif round_num == 3:
            # advanced tradeoffs
            score += 4

        topic_scores[topic] = score

    return topic_scores


def choose_topic(
    topic_scores
):
    """
    Weighted random selection.

    Avoid always choosing
    same top topic.
    """

    if not topic_scores:
        return None

    topics = list(
        topic_scores.keys()
    )

    scores = list(
        topic_scores.values()
    )

    total = sum(scores)

    if total <= 0:
        return random.choice(topics)

    probabilities = [
        s / total
        for s in scores
    ]

    return random.choices(
        topics,
        weights=probabilities,
        k=1
    )[0]


def choose_subtopic(
    concept_map,
    topic,
    covered_concepts
):

    candidates = concept_map.get(
        topic,
        []
    )

    if not candidates:
        return topic

    unused = [
        c for c in candidates
        if c not in covered_concepts
    ]

    if unused:
        return random.choice(unused)

    return random.choice(
        candidates
    )


def interview_brain(
    profile,
    job_description,
    state
):

    # ----------------------
    # SAFETY
    # ----------------------
    state.setdefault(
        "topics_asked",
        []
    )

    state.setdefault(
        "concepts_covered",
        []
    )

    state.setdefault(
        "question_types",
        []
    )

    round_num = state.get(
        "round",
        1
    )

    step = state.get(
        "step",
        0
    )

    # ----------------------
    # CONCEPT MAP
    # ----------------------
    concept_map = profile.get(
        "interview_concepts",
        {}
    )

    if not concept_map:

        concept_map = {
            "General Engineering": [
                "problem solving",
                "debugging",
                "system thinking"
            ]
        }

    # ----------------------
    # DIFFICULTY
    # ----------------------
    difficulty = choose_difficulty(
        round_num,
        step
    )

    # ----------------------
    # QUESTION TYPE
    # ----------------------
    question_type = (
        select_question_type(
            round_num,
            state[
                "question_types"
            ]
        )
    )

    # ----------------------
    # TOPIC SELECTION
    # ----------------------
    topic_scores = score_topics(
        concept_map,
        job_description,
        state[
            "topics_asked"
        ],
        round_num
    )

    topic = choose_topic(
        topic_scores
    )

    # ----------------------
    # SUBTOPIC
    # ----------------------
    subtopic = choose_subtopic(
        concept_map,
        topic,
        state[
            "concepts_covered"
        ]
    )

    # ----------------------
    # MEMORY UPDATE
    # ----------------------
    state[
        "topics_asked"
    ].append(topic)

    state[
        "concepts_covered"
    ].append(subtopic)

    state[
        "question_types"
    ].append(
        question_type
    )

    return {
        "topic": topic,
        "subtopic": subtopic,
        "question_type": question_type,
        "difficulty": difficulty,
        "state": state
    }