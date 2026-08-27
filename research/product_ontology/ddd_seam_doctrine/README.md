# DDD product and seam doctrine

This corpus prevents a common category error in the product ontology: treating domain, subdomain,
bounded context, aggregate, library, service, deployment, team and product as one decomposition.
They are related graphs with different identity laws.

```text
problem space                         solution and adoption space

domain                               user problem / outcome
  -> subdomain                              -> product
       -> model candidate                         -> capability requirements
            -> bounded context                         -> provider offers
                 -> aggregate
                 -> domain service
                 -> module/library seam
```

The arrows are not equivalences. One product may compose several bounded contexts. One bounded
context may contain several aggregates and libraries or support several products. A library can be
a reusable published language or algorithm without becoming a bounded context or product.

## Research conclusion

DDD is an evolutionary method for making a domain model operational in language and code. Its
strategic contribution is not a standard folder structure; it is the explicit applicability of
multiple internally coherent models and the map of translations and influence between them. Eric
Evans' conceptual-contours rule further rejects both arbitrary fine-grained decomposition and
monolithic lumping: seams should follow domain divisions plus observed axes of change and
stability.

Product derivation is a separate pass. Products start from a defined user, problem, independent
outcome, adoption and exit boundary, then add ownership, service levels, lifecycle, evidence and
economics. Product and DDD evidence are joined only after both have been derived independently.

## Correct order

```text
real cases and domain evidence
  -> language conflicts and rules
  -> coherent model candidates
  -> bounded contexts and context map
  -> aggregates, services and conceptual contours
  -> semantic/algorithm/effect library seams

users, jobs and outcomes
  -> independent adoption/operation/exit promises
  -> product candidates

both graphs
  -> product × context × capability × library × provider hypergraph
  -> falsification, implementation and qualification
```

The machine-readable procedure, seam forces and negative tests are generated beside this file.
The first applied audit corrects Metadata Discovery from six mechanically one-per-library contexts
to three model boundaries while retaining six exact library seams and one operated product.

## Evidence

- [Eric Evans, DDD Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [Martin Fowler, Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Martin Fowler, Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)
- [Alberto Brandolini, EventStorming](https://www.eventstorming.com/)
- [Team Topologies, Organization Dynamics](https://teamtopologies.com/s/Organization-Dynamics-with-Team-Topologies-Mini-book-MB80.pdf)
- [Thoughtworks, Designing Data Products](https://martinfowler.com/articles/designing-data-products.html)
