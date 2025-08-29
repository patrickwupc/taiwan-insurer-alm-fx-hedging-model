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
- **Interest Rates** – Daily interest rates for both the U.S. and Taiwan. And using the interest rate parity formula, we derive the 3m, 6m, and 1y forwad rates and spots. Backtesting it against the spot rates shows accuracy
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

📌 Project Status
Current Progress & Key Achievements
Data Integration & Validation: Successfully collected, aligned, and validated financial data on a daily frequency, confirming consistency with interest rate parity.

Core Model Development: Constructed the Insurer class and core functions to simulate the financial performance of a life insurer's portfolio under various market conditions.

Foundational Simulation: Built and executed a time-series simulation framework to analyze a range of insurer profiles and hedging strategies.

🚀 Future Enhancements
Comprehensive Scenario Analysis: Expanding the simulation to evaluate the impact of a wider range of hedging ratios and market scenarios.

Advanced Hedging Strategy Integration: Incorporating and assessing the effectiveness of alternative instruments, including:

Cross-currency swaps

Options

Non-Deliverable Forwards (NDFs)

FEVR Integration: Developing a new model component to manage and project the FX Valuation Reserve (FEVR), aiming to align the framework with Taiwan's regulatory standards.

Enhanced Visualization: Creating more interactive and detailed charts to present complex findings and key trade-offs.