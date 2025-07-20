% ASEKE Cognitive Architecture - Base Knowledge Structures
% Implementing concepts from the ASEKE system and Curiosity Loop

% ============================================
% KNOWLEDGE SUBSTRATE (KS) - Core Domain Facts
% ============================================

% Basic Knowledge Entities
knowledge_entity(concept).
knowledge_entity(fact).
knowledge_entity(rule).
knowledge_entity(theory).
knowledge_entity(belief).

% Knowledge Substrate Properties
substrate_property(domain, photosynthesis).
substrate_property(density, high).
substrate_property(accessibility, public).
substrate_property(structure, hierarchical).

% Information Structures (IS)
information_structure(photosynthesis, process).
information_structure(calvin_cycle, sub_process).
information_structure(light_reactions, sub_process).
information_structure(glucose, molecule).
information_structure(co2, molecule).

% ============================================
% EMOTIONAL STATE ALGORITHMS (ESA) - Plutchik's Emotions
% ============================================

% Basic Emotions (Plutchik's wheel)
emotion(joy).
emotion(trust).
emotion(fear).
emotion(surprise).
emotion(sadness).
emotion(disgust).
emotion(anger).
emotion(anticipation).

% Emotional Intensity Levels
intensity(low).
intensity(medium).
intensity(high).

% Emotional State Modulation
emotional_state(current_emotion, trust, medium).
emotional_state(learning_context, curiosity, high).
emotional_state(knowledge_gap, surprise, medium).

% ============================================
% SOCIOBIOLOGICAL DRIVE ALGORITHMS (SDA)
% ============================================

% Basic Drives
drive(belonging).
drive(status).
drive(reciprocity).
drive(kin_selection).
drive(conformity).
drive(truth_seeking).

% Drive States
drive_state(truth_seeking, active, high).
drive_state(belonging, active, medium).
drive_state(status, dormant, low).

% ============================================
% COGNITIVE ENERGY (CE) Management
% ============================================

% Energy Types
energy_type(intellectual).
energy_type(emotional).
energy_type(motivational).

% Current Energy Levels
energy_level(intellectual, 85).
energy_level(emotional, 70).
energy_level(motivational, 90).

% Energy Allocation Rules
allocate_energy(learning_task, intellectual, 40).
allocate_energy(learning_task, emotional, 20).
allocate_energy(learning_task, motivational, 30).

% ============================================
% CURIOSITY LOOP - Dynamic Knowledge Acquisition
% ============================================

% Knowledge Gap Detection
knowledge_gap(calvin_cycle, key_enzyme).
knowledge_gap(photosynthesis, location_specifics).
knowledge_gap(light_reactions, energy_conversion).

% Inquiry Generation Rules
generate_inquiry(Gap) :-
    knowledge_gap(Domain, Gap),
    \+ known_fact(Domain, Gap),
    energy_level(intellectual, Level),
    Level > 50.

% Known Facts (to test against gaps)
known_fact(photosynthesis, process_type).
known_fact(photosynthesis, input_molecules).
known_fact(photosynthesis, output_molecules).

% Research Priority Calculation
research_priority(Gap, Priority) :-
    knowledge_gap(Domain, Gap),
    importance_score(Domain, DomainScore),
    urgency_score(Gap, UrgencyScore),
    Priority is DomainScore * UrgencyScore.

importance_score(photosynthesis, 9).
importance_score(calvin_cycle, 8).
importance_score(light_reactions, 8).

urgency_score(key_enzyme, 9).
urgency_score(location_specifics, 7).
urgency_score(energy_conversion, 8).

% ============================================
% META-COGNITIVE REGULATION
% ============================================

% Meta-cognitive States
metacognitive_state(monitoring, active).
metacognitive_state(evaluation, active).
metacognitive_state(regulation, moderate).

% Confidence Levels
confidence_level(photosynthesis_knowledge, 75).
confidence_level(biochemistry_knowledge, 60).
confidence_level(cellular_biology, 70).

% Learning Strategy Selection
learning_strategy(knowledge_gap_detected) :-
    emotional_state(_, surprise, _),
    drive_state(truth_seeking, active, _),
    select_strategy(targeted_research).

select_strategy(targeted_research).
select_strategy(broad_exploration).
select_strategy(deep_analysis).

% ============================================
% KNOWLEDGE INTEGRATION (KI) Rules
% ============================================

% Integration Compatibility
compatible_integration(X, Y) :-
    information_structure(X, Type1),
    information_structure(Y, Type2),
    compatible_types(Type1, Type2).

compatible_types(process, sub_process).
compatible_types(molecule, process).
compatible_types(sub_process, sub_process).

% Integration Success Probability
integration_probability(X, Y, Prob) :-
    compatible_integration(X, Y),
    confidence_level(Domain, Conf),
    emotional_state(learning_context, _, Intensity),
    intensity_value(Intensity, IntVal),
    Prob is (Conf + IntVal * 10) / 100.

intensity_value(low, 1).
intensity_value(medium, 2).
intensity_value(high, 3).

% ============================================
% QUERY EXAMPLES AND TESTS
% ============================================

% Test queries to demonstrate the system:
% ?- knowledge_gap(Domain, Gap).
% ?- research_priority(Gap, Priority).
% ?- generate_inquiry(Gap).
% ?- integration_probability(photosynthesis, calvin_cycle, Prob).
% ?- emotional_state(Context, Emotion, Level).
% ?- drive_state(Drive, State, Level).
% ?- energy_level(Type, Level).