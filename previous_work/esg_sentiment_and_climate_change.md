# ESG Sentiment and Climate Change: An Analysis of the Effects of Climate Disaster Exposure on ESG Reports

## Authors
- Ibrahim Ben Araar
- Juliana Ludemann
- Lennart Schreiber
- Nour Ouljihate

## Research Question
How does climate disaster exposure affect the language and sentiment of corporate ESG reports?

## Motivation
ESG reporting has become an important mechanism through which firms communicate environmental and social risks to investors.

This project examines whether exposure to climate disasters changes how firms discuss climate-related risks and opportunities in ESG reports.

## Data

### Firm Sample
- Industrial firms (XLI Components) from the S&P 500
- ESG reports from 2021–2023
- U.S.-headquartered independent firms

### Disaster Exposure
A firm is considered exposed if:
- Its headquarters county experienced a FEMA-declared disaster
- Or a neighboring county experienced a disaster

### Additional Controls
- CEO educational background
- County-level climate beliefs

## NLP Analysis

### Climate Paragraph Extraction
Climate-related paragraphs are identified using a predefined keyword list.

Final dataset:
- 13,959 climate-related paragraphs

### Sentiment Classification

| Class | Score |
|---------|---------|
| Risk | -5 |
| Neutral | 0 |
| Opportunity | 5 |

## Estimation Strategy
The project uses a staggered Difference-in-Differences design.

## Results
Limited evidence suggests that disaster exposure causes firms to discuss climate-related opportunities more positively.

## Conclusion
Media exposure may amplify ESG responses, but evidence for a strong causal effect remains limited.
