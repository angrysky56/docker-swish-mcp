% Debug test for SWISH functionality
debug_fact(hello).
debug_fact(world).
debug_rule(X) :- debug_fact(X).