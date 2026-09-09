# Sources

The consolidated bibliography behind `taxonomy/techniques.json` and the three question banks. Every technique record carries a `sources` list of the ids below and a `confidence` field. This document explains what those confidence marks mean and lists every source in full. `taxonomy/reference.md` carries the same list alongside the human-readable technique writeups; this is the standalone version.

## Confidence marks

`confidence` in a technique record describes how well corroborated the technique itself is, not how reliable a given source is thought to be in general, and it does not reduce to a simple source count. The pattern across the taxonomy's 63 techniques:

- **high** (32 techniques): the 18 interrogation approaches (Catalog B, from FM 2-22.3 Chapter 8) and the 11 social-engineering and cyber vectors (Catalog C), each resting on a single authoritative doctrinal or industry source with no conflicting material, plus 3 elicitation techniques with especially broad corroboration.
- **corroborated** (23 techniques): the bulk of Catalog A, the elicitation techniques proper, corroborated across the FBI brochure, the OSAC guide, the NCSC job aid, the CDSE Accidental Conversations job aid (2025), the DCSA brochure (2021), and Army FM 34-60.
- **medium** (8 techniques): 2 elicitation techniques, Mirroring and Quote reported facts, that appear in only one corroborating source and carry a lower default scoring weight for the same reason; and all 6 collection methods (Catalog D), sourced from a CDSE and DCSA pair whose technique labels have not yet been independently cross-checked against a third source.

## Federal and doctrinal sources

1. `fbi-elicitation` - FBI, Elicitation brochure and "Eliciting Corporate Information" (Office of Private Sector). Corroborated via mirrors and OSAC; fbi.gov blocks automated fetching, so the brochure's full technique list still needs a read from the official PDF (see `docs/limitations.md`).
2. `osac-elicitation-guide-2018` - U.S. State Department OSAC, Elicitation guide, 2018. Verified via mirror.
3. `ncsc-elicitation-brochure` - NCSC/ODNI, Elicitation brochure (S443-004) and Foreign Collection Methods: Indicators and Countermeasures. Verified.
4. `ncsc-nevernight-safeguarding-academia` - NCSC/ODNI, The Nevernight Connection (2020), the Safeguarding Academia Quick Reference Guide (August 2025), and the Safeguarding Science Toolkit. Verified.
5. `cdse-accidental-conversations-2025` - CDSE/DCSA, Accidental Conversations: Elicitation Techniques and the Science Behind Them (2025). Reached via mirror and proxy; cdse.edu and dcsa.mil block direct fetching.
6. `cdse-foreign-collection-methods-2024` - CDSE/DCSA, Foreign Collection Methods job aid (December 2024). Reached via mirror and proxy.
7. `dcsa-elicitation-brochure-2021` - DCSA, Elicitation brochure (2021). Reached via mirror and proxy.
8. `cdse-ci116-student-guide-2024` - CDSE, CI116 Counterintelligence Awareness and Reporting Student Guide (October 2024). Reached via mirror and proxy.
9. `dcsa-targeting-us-technologies-2025` - DCSA, Targeting U.S. Technologies (DCSA-TA-25-001, FY24 report). Reached via proxy.
10. `dodd-5240-06` - DoD Directive 5240.06, Counterintelligence Awareness and Reporting (2011, including Change 3, 2020). The key item text is high confidence; the exact table numbering and the Article 92 cut-lines still need verification against a clean PDF, since two extractions disagreed.
11. `fm-2-22-3` - FM 2-22.3, Human Intelligence Collector Operations (2006), Chapter 8. Parsed from the primary PDF.
12. `fm-34-60` - FM 2-22.2 / FM 34-60, Counterintelligence (2009 / 1995). Parsed in a prior research pass.
13. `ar-381-12` - AR 381-12, Threat Awareness and Reporting Program (2016; retitled and reissued July 2025, that edition's wording not yet verified). Parsed from the 2016 edition.
14. `atp-2-22-9` - ATP 2-22.9, Open-Source Intelligence (2012). Parsed.
15. `icd-304-icd-750` - ICD 304 (Human Intelligence) and ICD 750 (Counterintelligence Programs). Verified.
16. `jp-3-13-2-jp-2-0` - JP 3-13.2 (Military Information Support Operations) and JP 2-0 (Joint Intelligence). Verified.
17. `service-department-ci-sources` - Service and department sources of mixed confidence: AFI 71-101 Volume 4 and AFOSI materials (Air Force); NCIS handouts and NTTP 3-13.3 (Navy and Marine Corps); the DTRA in-processing briefing; DOE/NNSA Counterintelligence Reporting Requirements; and the NITTF minimum standards.
18. `cisa-social-engineering-guidance` - CISA, Insider Threat Mitigation Guide and social-engineering guidance.
19. `mitre-attack-t1566` - MITRE ATT&CK, technique T1566 (Phishing) and its sub-techniques.
20. `mitre-ctid-insider-threat-ttp-kb` - MITRE Center for Threat-Informed Defense, Insider Threat TTP Knowledge Base (Apache-2.0, machine readable).
21. `enisa-threat-landscape-social-engineering` - ENISA Threat Landscape, social-engineering section.
22. `nist-sp-800-53-at-2-3-800-50` - NIST SP 800-53 control AT-2(3), "social engineering and mining," and NIST SP 800-50 Revision 1.
23. `fbi-ic3` - FBI Internet Crime Complaint Center (IC3), cited for whaling and business email compromise reporting (ic3.gov).

## Academic and framework sources

24. `haisq-sebis-ttat-instruments` - The HAIS-Q, SeBIS, and TTAT susceptibility-instrument literature. The self-assessment module adapts item structure from this line rather than reusing scale items verbatim; see `docs/limitations.md` on the pending license check.
25. `granhag-scharff` - Granhag, Montecinos, Oleszkiewicz, and colleagues, the Scharff technique study series (2014 to 2019). The primary evidence base for the A28 composite technique.
26. `luke-granhag-meta-analysis-2020` - Luke and Granhag, meta-analysis of the Scharff technique studies (2020). Pooled effect sizes for that meta-analysis are still an open verification item (`docs/limitations.md`).
27. `rantamaki-2020-scharff-forewarning` - Rantamaki et al. (2020), forewarning against the Scharff technique. Found that simply telling people about the Scharff counter-strategy did not reliably help them resist it, which is why the knowledge module trains a practiced response rather than a one-time warning.
28. `caputo-danley-ratcliff-2024` - Caputo, Danley, and Ratcliff (2024), skills-based versus awareness-based training randomized controlled trial, Frontiers in Psychology. The evidence behind grading the knowledge module as recognize-and-respond drills with feedback rather than a one-shot quiz.
29. `van-der-kleij-2023-reciprocity` - Van der Kleij et al. (2023, N = 2,426), disclosure under reciprocity and authority. The evidence anchor for reciprocity's heavier default class weight; see `docs/scoring.md`. Full-text verification of the precise effect size and its moderators is an open item.
30. `alison-orbit-meissner-hig` - Alison and Alison, the ORBIT model; Meissner et al., the High-Value Detainee Interrogation Group (HIG) research program reviews.
31. `elm-inoculation-reactance-influence-theory` - Petty and Cacioppo, the Elaboration Likelihood Model; McGuire, and Banas and Rains, inoculation theory; Brehm, reactance theory; Burkett, MICE to RASCLS (CIA Studies in Intelligence, 2013); Cialdini, principles of influence.

## Self-assessment item-level citations

The self-assessment bank (`taxonomy/banks/self_assessment.json`) cites eleven items against the specific technique write-up within source 5 (`cdse-accidental-conversations-2025`) rather than the document as a whole, since each item mirrors one technique from that job aid.

32. `cdse-elicitation-flattery-a1` - CDSE/DCSA, Accidental Conversations (2025), the Flattery (A1) technique entry.
33. `cdse-elicitation-provocation-a2` - CDSE/DCSA, Accidental Conversations (2025), the Provocation / feigned incredulity (A2) technique entry.
34. `cdse-elicitation-false-statement-a3` - CDSE/DCSA, Accidental Conversations (2025), the Deliberate false statement (A3) technique entry.
35. `cdse-elicitation-good-listener-a9` - CDSE/DCSA, Accidental Conversations (2025), the Good listener (A9) technique entry.
36. `cdse-elicitation-assumed-knowledge-a12` - CDSE/DCSA, Accidental Conversations (2025), the Assumed knowledge (A12) technique entry.
37. `cdse-elicitation-bracketing-a13` - CDSE/DCSA, Accidental Conversations (2025), the Bracketing (A13) technique entry.
38. `cdse-elicitation-direct-question-a19` - CDSE/DCSA, Accidental Conversations (2025), the Direct question / survey (A19) technique entry.
39. `cdse-elicitation-urge-to-complain-a23` - CDSE/DCSA, Accidental Conversations (2025), the Exploiting the urge to complain (A23) technique entry.
40. `cdse-elicitation-offering-assistance-a25` - CDSE/DCSA, Accidental Conversations (2025), the Offering assistance (A25) technique entry.
41. `cdse-elicitation-hypothetical-situation-a26` - CDSE/DCSA, Accidental Conversations (2025), the Hypothetical situation (A26) technique entry.
42. `cdse-elicitation-setting-manipulation-a27` - CDSE/DCSA, Accidental Conversations (2025), the Setting manipulation (A27) technique entry.

## Adjacent sources not tied to a specific technique id

The MITRE ATT&CK, CTID, ENISA, and NIST entries above (19, 20, 21, 22) also frame Catalog C and Catalog D in `taxonomy/reference.md`: the social-engineering and cyber vectors, and the collection methods, that carry technique class `none` because they are delivery mechanisms rather than one of the four psychological classes.
