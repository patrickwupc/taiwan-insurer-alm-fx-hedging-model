# Taiwan Insurer FX Hedging Model

## 📌 Project Overview
This project is motivated by the **recent and abrupt appreciation of the New Taiwan Dollar (TWD)** and its significant impact on the financial health of Taiwanese life insurers.  
This event—often referred to in local financial news as a *“19-sigma event”*—highlighted the **substantial risks of managing large foreign asset portfolios**.

These risks are further compounded by **ongoing geopolitical tensions** and **shifting tariff policies**, which can trigger **unexpected capital flows** and **currency volatility**. The need for **robust FX hedging strategies** has never been more critical.

The aim of this project is to build a **stylized financial model** of a typical Taiwanese life insurance company to:
- **Simulate** the impact of FX rate fluctuations and hedging strategies on profitability and capital.
- **Analyze** the performance of foreign assets, particularly **long-term U.S. corporate bonds**.
- **Evaluate** the effectiveness and cost of different hedging ratios using spot and forward market data.

The final deliverable will be a **simulation framework** to help:
- Understand the financial dynamics reported by Taiwan’s **Financial Supervisory Commission (FSC)**.
- Assess the **efficacy of various hedging instruments** under different market conditions.

---

## 📊 Data
This project utilizes **real-world financial data**:

- **TWD/USD Exchange Rates** – Daily spot rates.  
- **Forward Market Data** – Daily 3-month, 6-month, and 1-year forward rates and points.  
- **Interest Rates** – Daily interest rates for both the U.S. and Taiwan.  
- **U.S. Corporate Bond Yields** – Daily yields for:
  - ICE BofA 7–10 Year U.S. Corporate Index (`BAMLC4A0C710YEY`)
  - ICE BofA 10–15 Year U.S. Corporate Index (`BAMLC4A0C1015YEY`)  

These serve as robust proxies for the **high-quality long-term corporate bonds** typically held by Taiwanese insurers.

---

## 🛠 Methodology
The project structure is designed for **clarity and reusability**:

- **Python Class** – [`src/insurer_model.py`]  
  The core `Insurer` class holds financial parameters and methods to simulate daily financial events.  
  Simulations will be run in `02_model_development.ipynb`, using insurer profiles (asset breakdowns, holdings, and hedging strategies) representative of various approaches observed in Taiwan.

- **Jupyter Notebooks** – [`notebooks/`]  
  Used for:
  - Data acquisition and cleaning
  - Running simulations
  - Generating analysis and visualizations

---

## 📌 Current Progress & Key Observations
- **Data Acquisition** – All necessary financial data has been collected and aligned to a **daily frequency**.
- **Validation** – Initial checks confirm that forward points are **consistent with interest rate parity**.

---

## 🚀 Next Steps
1. **Build the `Insurer` Class**  
   Implement core methods for calculating bond returns and applying hedging strategies.

2. **Develop the Simulation Framework**  
   Run daily simulations to analyze different insurer profiles.

3. **Scenario Analysis**  
   Evaluate the impact of different hedging ratios (e.g., **50% vs 70%**).

4. **Visualize Results**  
   Create clear and informative charts to present findings.

5. **Hedging Instrument Testing**  
   Incorporate and assess the effectiveness of:
   - Cross-currency swaps
   - Options
   - Non-Deliverable Forwards (NDFs)  
   in mitigating portfolio losses during FX volatility.