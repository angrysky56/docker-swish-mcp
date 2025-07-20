% Logic Programming Examples and Rules
% Demonstrating different Prolog programming patterns

% ============================================
% FACTS - Basic Information
% ============================================

% Family relationships
parent(tom, bob).
parent(tom, liz).
parent(bob, ann).
parent(bob, pat).
parent(liz, jim).

% Gender information
male(tom).
male(bob).
male(jim).
female(liz).
female(ann).
female(pat).

% Simple facts
likes(bob, programming).
likes(ann, logic).
likes(jim, puzzles).
likes(liz, books).

% ============================================
% RULES - Logical Relationships
% ============================================

% Family relationship rules
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).

% Grandparent relationships
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
grandfather(X, Z) :- grandparent(X, Z), male(X).
grandmother(X, Z) :- grandparent(X, Z), female(X).

% Sibling relationships
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.

% Ancestor relationships (recursive)
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% ============================================
% UTILITY PREDICATES
% ============================================

% Check if someone is happy (likes something)
happy(X) :- likes(X, _).

% Find all children of a parent
children_of(Parent, Children) :-
    findall(Child, parent(Parent, Child), Children).

% Count number of children
child_count(Parent, Count) :-
    children_of(Parent, Children),
    length(Children, Count).

% ============================================
% LOGIC PUZZLE RULES
% ============================================

% Classic logic programming: list membership
list_member(X, [X|_]).
list_member(X, [_|T]) :- list_member(X, T).

% List length calculation
list_length([], 0).
list_length([_|T], N) :- 
    list_length(T, N1), 
    N is N1 + 1.

% List append operation
list_append([], L, L).
list_append([H|T1], L, [H|T2]) :- 
    list_append(T1, L, T2).

% ============================================
% EXAMPLE QUERIES TO TRY
% ============================================
% After consulting this file, try these queries:
%
% Basic facts:
% ?- parent(tom, bob).
% ?- likes(bob, programming).
%
% Rules:
% ?- father(tom, bob).
% ?- grandfather(tom, ann).
% ?- sibling(bob, liz).
%
% Find all solutions:
% ?- findall(X, parent(tom, X), Children).
% ?- findall(X, happy(X), HappyPeople).
%
% Recursive relationships:
% ?- ancestor(tom, ann).
% ?- ancestor(tom, X).
%
% List operations:
% ?- list_member(3, [1,2,3,4,5]).
% ?- list_length([a,b,c,d], N).
% ?- list_append([1,2], [3,4], Result).
