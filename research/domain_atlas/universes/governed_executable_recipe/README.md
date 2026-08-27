# Governed executable-recipe semantics

This universe owns reusable recipe definition, lifecycle, edit-history, replay and target-
preparation mechanics. It is not a workflow scheduler, data-preparation product, inspection
product, transformation engine or machine controller.

```text
step contracts + typed parameters + graph/failure/loss policy
                           |
                           v
               recipe-definition compiler
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
 lifecycle registry   edit-history      replay planner
                           |                |
                           |                v
                           |          replay evaluator
                           |
released recipe -----------+------> target-preparation protocol
                                      |
                                      v
                     effect request -> external target runtime
                                      |
                                      v
                       receipt + observed prepared-state reconciliation
```

Exact libraries:

1. `library.recipe.definition.compiler`
2. `library.recipe.lifecycle.registry`
3. `library.recipe.edit_history.algebra`
4. `library.recipe.replay.planner`
5. `library.recipe.replay.evaluator`
6. `library.recipe.target_preparation.protocol`

Inspection defect/tolerance semantics and preparation transformation semantics remain product-local
or owned by referenced step contracts. A compiled recipe is not released; released is not prepared;
prepared is not executed; executed is not accepted. Undo moves a history cursor and does not erase
the edit occurrence. Replay requires a completely bound plan rather than a filename and a seed.
Every implementation remains unqualified.
