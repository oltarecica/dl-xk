# Project Idea

## Where the Lights Went Out: Mapping Depopulation in Kosovo with CNN Prediction Errors

---

## The Idea

We have two datasets for Kosovo:
- A satellite image of nighttime lights — how bright each area is
- A dataset showing how much of each area is covered by buildings (built-up surface)

We train a CNN that looks at a patch of the nighttime lights image and predicts how built-up that area is. It learns that bright areas tend to be more built-up.

**Why the errors are interesting:**
Some areas are more built-up than the light would suggest. The model sees darkness and predicts "not much built here" — but actually there are lots of buildings. Those are the red areas on the map. The interpretation: buildings exist, but nobody's home. Vacancy, depopulation, emigration.

**Why CNN and not a simple formula:**
A CNN picks up on spatial patterns in the light data — halos around city centres, road corridors, radial gradients — that a simple regression would miss. That's what makes it a valid deep learning project.

**The story:**
> "We trained a model to predict development from light. Where it's systematically wrong, we find the fingerprint of depopulation — and it matches what Kosovo's 2024 census found."
