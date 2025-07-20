% ASEKE Cognitive Architecture - Corrected Implementation
% Systematic approach based on methodological analysis

% ============================================
% KNOWLEDGE SUBSTRATE (KS) - Core Domain Facts  
% ============================================

% Basic knowledge entities
knowledge_entity(concept).
knowledge_entity(fact).
knowledge_entity(rule).
knowledge_entity(theory).

% Photosynthesis knowledge base
process(photosynthesis).
location(photosynthesis, chloroplast).
input_molecule(photosynthesis, carbon_dioxide).
input_molecule(photosynthesis, water).
input_molecule(photosynthesis, light_energy).
output_molecule(photosynthesis, glucose).
output_molecule(photosynthesis, oxygen).

% Sub-processes
subprocess(photosynthesis, light_reactions).
subprocess(photosynthesis, calvin_cycle).
location(light_reactions, thylakoid_membrane).
location(calvin_cycle, stroma).

% ============================================
% CURIOSITY LOOP IMPLEMENTATION
% ============================================

% Knowledge gap detection
knowledge_gap(calvin_cycle, key_enzyme).
knowledge_gap(photosynthesis, efficiency_rate).
knowledge_gap(light_reactions, electron_transport).

% Gap detection predicate
detect_knowledge_gap(Domain, Gap) :-
    knowledge_gap(Domain, Gap),
    \+ has_knowledge(Domain, Gap).

% Current knowledge state
has_knowledge(photosynthesis, process_type).
has_knowledge(photosynthesis, location).
has_knowledge(photosynthesis, inputs).
has_knowledge(photosynthesis, outputs).

% Inquiry generation rule
generate_inquiry(Domain, Gap, Query) :-
    detect_knowledge_gap(Domain, Gap),
    atomic_list_concat(['What is the', Gap, 'for', Domain, '?'], ' ', Query).

% ============================================
% EMOTIONAL STATE ALGORITHMS (ESA)
% ============================================

% Plutchik's basic emotions
emotion(joy).
emotion(trust).
emotion(fear).
emotion(surprise).
emotion(sadness).
emotion(disgust).
emotion(anger).
emotion(anticipation).

% Current emotional state
emotional_state(curiosity, high).
emotional_state(confidence, medium).
emotional_state(engagement, high).

% ============================================
% META-COGNITIVE MONITORING
% ============================================

% System state assessment
system_state(knowledge_base_loaded, true).
system_state(consultation_working, true).
system_state(query_execution, functional).

% Confidence assessment
confidence_level(photosynthesis_domain, 75).
confidence_level(biochemistry_general, 60).
confidence_level(logic_programming, 85).

% ============================================
% TEST QUERIES
% ============================================

% Test basic facts
test_basic_facts :-
    process(photosynthesis),
    location(photosynthesis, chloroplast),
    write('Basic facts verified'), nl.

% Test curiosity loop
test_curiosity_loop :-
    detect_knowledge_gap(calvin_cycle, key_enzyme),
    generate_inquiry(calvin_cycle, key_enzyme, Query),
    format('Generated inquiry: ~w~n', [Query]).

% Test system integration
test_system_integration :-
    test_basic_facts,
    test_curiosity_loop,
    write('System integration test completed'), nl.