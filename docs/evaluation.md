# Evaluate a speech profile

Test whether listeners transcribe codes more accurately under the conditions where the codes will be used. The built-in English penalties are hypotheses, and each channel or language may need its own profile.

1. **Choose the setting.** Specify the language, speaker and listener populations, recording and playback conditions, and whether the handoff is in person or over a phone call. Set safe playback levels.
2. **Match the guessing probability.** Fix the code length and record the optimized generator's actual `candidate_count`. Create a control pool by sampling that many distinct strings uniformly from the full decimal space. Draw test strings uniformly from each pool. Use synthetic values throughout.
3. **Randomize the trials.** Mix the optimized and control samples without telling listeners which is which. Balance both conditions across speakers, listeners, and noise settings. Give both arms the same instructions and playback allowances.
4. **Measure the handoff.** Record first-attempt exact matches, requests for repetition, and time to correct entry. Preserve leading zeros in transcripts. Report sample sizes and uncertainty, and account for repeated trials with the same speakers or listeners.
5. **Validate on held-out sessions.** Use development sessions to choose penalties for error-prone digits or adjacent pairs. Compare the resulting profile with the control pool on held-out speakers and listeners before reporting an improvement.

Keep live verification codes and real customer recordings out of a benchmark. Aggregate results by condition when sharing the study.
