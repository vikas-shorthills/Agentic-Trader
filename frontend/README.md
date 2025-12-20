# 💼 Trade Analysis Platform

A modern React application for investment portfolio management and trading analysis, built with Vite, React, and Tailwind CSS.

## 🚀 Features

### 📱 Screens

1. **Home** - Investment Portfolio Builder
   - Add multiple companies to your investment bucket
   - Set investment tenure (weeks)
   - Specify investment amount
   - View real-time investment summary with projections

2. **Arena** - Trading Arena
   - Real-time stock market data
   - Top stocks overview
   - Interactive stock details modal
   - Market status and metrics

3. **Value Analysis** - Fundamental Analysis
   - Compare companies using key metrics (P/E, P/B, D/E, ROE, Dividend Yield)
   - Interactive metric selection
   - Company ratings and recommendations
   - Best value insights

4. **Trade Analysis** - Performance Tracking
   - Track all your trades
   - Performance metrics (Win rate, P&L, Returns)
   - Timeframe analysis (1D to ALL)
   - Trading insights and recommendations

## 🛠️ Tech Stack

- **React 18** - Modern UI library
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Router DOM** - Client-side routing

## 📁 Project Structure

```
frontend_trade/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.jsx          # Main layout wrapper
│   │   │   └── Navigation.jsx      # Navigation bar
│   │   └── home/
│   │       ├── CompanyInput.jsx    # Company bucket input
│   │       └── InvestmentSummary.jsx  # Investment summary display
│   ├── pages/
│   │   ├── Home.jsx                # Home page
│   │   ├── Arena.jsx               # Arena page
│   │   ├── ValueAnalysis.jsx       # Value analysis page
│   │   └── TradeAnalysis.jsx       # Trade analysis page
│   ├── App.jsx                     # Main app component
│   ├── main.jsx                    # App entry point
│   └── index.css                   # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🚦 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository or navigate to the project directory:
```bash
cd /home/shtlp_0170/Videos/frontend_trade
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will open automatically in your browser at `http://localhost:3000`.

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 🎨 Design Features

- **Modern UI** - Clean, professional design with gradient backgrounds
- **Responsive** - Works seamlessly on desktop, tablet, and mobile
- **Interactive** - Smooth transitions and hover effects
- **Accessible** - Semantic HTML and ARIA labels
- **Color-coded** - Visual feedback with meaningful colors

## 📊 Features Details

### Home Screen
- **Dynamic Company Input**: Add/remove companies with real-time validation
- **Investment Calculator**: Automatic calculation of per-company allocation
- **Projected Returns**: 8% annual return projection
- **Investment Breakdown**: Visual summary of your portfolio

### Arena
- **Live Market Data**: View top stocks with real-time prices
- **Stock Details Modal**: Detailed view of individual stocks
- **Market Overview**: Track market status, gainers, losers, and volume

### Value Analysis
- **Multiple Metrics**: Compare P/E, P/B, D/E, ROE, and Dividend Yield
- **Interactive Selection**: Highlight specific metrics for comparison
- **Rating System**: Strong Buy, Buy, Hold recommendations
- **Best Value Insights**: Automated analysis of top performers

### Trade Analysis
- **Performance Metrics**: Win rate, total P&L, average return
- **Trade History**: Complete list of all trades with P&L
- **Timeframe Filters**: View performance over different periods
- **Insights & Recommendations**: AI-powered trading suggestions

## 🎯 Usage Tips

1. **Home Page**: Start by adding your favorite companies, set your investment horizon, and see projected returns
2. **Arena**: Monitor market movements and explore stock details
3. **Value Analysis**: Compare fundamental metrics to find undervalued stocks
4. **Trade Analysis**: Track your trading performance and get actionable insights

## 🔧 Customization

### Tailwind Configuration
Modify `tailwind.config.js` to customize colors, spacing, and other design tokens.

### API Integration
Replace mock data in pages with real API calls for live market data.

### Additional Features
- Add user authentication
- Integrate real-time market data APIs
- Add charting libraries (Chart.js, Recharts)
- Implement portfolio tracking
- Add export functionality (PDF, CSV)

## 📝 License

This project is open source and available for personal and commercial use.

## 👨‍💻 Development

Built with modern React best practices:
- Functional components with hooks
- Component composition
- Responsive design patterns
- Clean code architecture

---

**Happy Trading! 📈💰**

