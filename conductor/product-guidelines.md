# Product Guidelines: Omnix

## Tone and Voice
- **The "Professional Sidekick":** Omnix balances tactical precision with encouraging support. It should speak like an experienced co-op partner—concise and data-driven when strategy is needed, but friendly and supportive to keep the session enjoyable.
- **Actionable & Direct:** Avoid fluff. Responses should prioritize utility and speed, helping the user make better decisions in real-time.

## Visual Identity & UX
- **Modern Gaming HUD:** The UI should feel premium and integrated while using a restrained dark palette, clear hierarchy, and one cool accent instead of visual noise.
- **Smart Information Density:** Layouts should be compact and information-dense, maximizing the visibility of stats, logs, and tips without overwhelming the screen.
- **Immersive Non-Distraction:** While the design is bold, the overlay must never block critical game information. Use transparency and minimize transitions to stay out of the user's way.

## Development Principles
- **Extreme Modularity:** Core services (detection, automation, AI, capabilities, and persistence) remain decoupled. Circular dependencies are strictly prohibited.
- **Privacy by Design:** Local-first is the law. All AI operations, gameplay logs, and session data default to local storage. Any remote connection must be explicitly configured and approved by the user.
- **Fail-Safe Robustness:** The application must remain responsive regardless of AI inference speed or background task load. Unsupported platform features must be visibly disabled with a reason, never silently degraded.

## User Engagement
- **Transparency:** Clearly communicate when the AI is processing or when a macro is active.
- **Customization:** Empower the user to tailor the overlay's density and the AI's "chatty-ness" to their preference.
