//! HRM-style structured reasoning: optional prompt augmentation for complex questions.
//! No neural model - template-based only.

const REASONING_PREFIX: &str = "Think through this step by step. Consider options, then give a clear recommendation.";

pub fn reasoning_prefix_for_question(question: &str) -> Option<&'static str> {
    let q = question.to_lowercase();
    let triggers = [
        "how should i",
        "what is the best way",
        "help me solve",
        "step by step",
        "walk me through",
        "best strategy",
        "optimal",
        "most efficient",
        "how do i solve",
    ];
    if triggers.iter().any(|t| q.contains(t)) {
        Some(REASONING_PREFIX)
    } else {
        None
    }
}
