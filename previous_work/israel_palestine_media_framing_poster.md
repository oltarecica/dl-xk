# Media Framing in the News on the Israeli–Palestine Conflict Using NLP Techniques

## Authors

Elif Çanga, Yagmur Helin Aslan

## Research Question

How do BBC and Al Jazeera frame the Israeli–Palestinian conflict through language and reporting choices?

## Motivation

The study investigates how media framing differs between:
- BBC (United Kingdom)
- Al Jazeera (Qatar)

The conflict received extensive global attention after 7 October 2023, making language choices especially important.

## Data

### Sources
- BBC News
- Al Jazeera

### Period
7 October 2023 – 31 December 2023

### Dataset

- 1,645 news articles
  - 685 BBC
  - 960 Al Jazeera
- 40,947 sentences

## Data Processing

- Removed non-alphanumeric characters.
- Cleaned and reparsed text.
- Created keyword dictionaries.
- Applied NLP methods.

## Methods

### 1. Keyword Analysis

Compared frequencies of terms such as:
- Genocide
- Zionism
- Antisemitism
- Hostage
- Captive

### 2. SpaCy Dependency Parsing

Used sentence structure to identify:
- Which side suffered casualties
- Active versus passive constructions

### 3. BERT Classification

- Generated labelled training data.
- Fine-tuned BERT for casualty classification.
- Achieved:
  - Accuracy: 0.95
  - F1 Score: 0.95

### 4. Direct vs Indirect Reporting

Measured how often casualty reports cited external sources.

## Main Findings

### Word Choice

Al Jazeera more frequently used:
- Genocide
- Zionism
- Captive

BBC more frequently used:
- Antisemitism
- Condemn
- Hostage

### Casualty Coverage

- BBC provided substantially more coverage of Israeli casualties.
- Al Jazeera provided more coverage of Palestinian casualties.

### Reporting Style

BBC used indirect reporting more often for Palestinian casualty counts.

Many reports referenced:
> Hamas-run health ministry

## Conclusions

1. BBC emphasised Hamas more frequently.
2. Significant differences exist in vocabulary choices.
3. Coverage of casualties differs between outlets.
4. Reporting style itself can act as a framing mechanism.

The authors conclude that NLP methods can reveal patterns of media framing, although human interpretation remains important.
