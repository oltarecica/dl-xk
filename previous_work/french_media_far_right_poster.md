# Amplification Cycle: Does French Media Coverage Promote the Far-Right Agenda?

## Authors

Rebecca Gramiscelli, Elsa Poupelin, Victoria Bel, Louis Marie

## Research Question

Does media coverage in France increasingly reflect or amplify the priorities of far-right political parties?

## Motivation

- Far-right politicians received substantial media exposure before the 2024 French legislative elections.
- Immigration, religion, and national identity have become central themes in far-right political discourse.
- The study examines whether these themes receive disproportionate media attention.

## Data

### Political Manifestos
- French presidential elections: 2017, 2022
- French legislative election: 2024
- Sources:
  - Promesses.fr
  - Regards Citoyens
  - Official party websites

### Media Data
- GDELT Project API
- 10 French news outlets
- Articles from the two months preceding each election

## Methodology

1. OCR using Amazon Textract.
2. NLP topic classification.
3. Topic dictionary based on Di Tella et al. (2023).
4. Grouped topics into 10 broad themes.
5. Compared:
   - Political manifesto themes
   - Media coverage themes
   - Far-right vote shares

## Key Findings

### Manifestos

Far-right parties place greater emphasis on:
- Immigration
- Religion
- National identity

Other parties focus more on:
- Human rights
- Environment
- Foreign affairs

### Media Coverage

- Far-right politicians receive increasing media attention.
- Media attention and far-right vote share increased together between 2017 and 2024.

### Political–Media Alignment

- Overall alignment between manifesto priorities and media coverage is limited.
- Immigration-related themes appear overrepresented relative to non–far-right manifestos.

## Conclusion

- Far-right actors have become more visible in French media.
- Evidence does not conclusively show normalisation of far-right agendas.
- Media coverage displays selective emphasis on certain topics.
- Further work should include:
  - Sentiment analysis
  - Topic modelling (LDA)
  - Broader media sources
  - Longer time horizons
