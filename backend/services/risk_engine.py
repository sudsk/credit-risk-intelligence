async def _calc_alternative_data_score(self, sme_id: str, sme: pd.Series) -> float:
    """
    Calculate Alternative Data Score (15% of total) using ACTUAL data sources
    
    Sub-components:
    - Employee Signals (35%)
    - Web Traffic Signals (30%)
    - News Sentiment (20%)
    - Companies House Flags (15%)
    """
    
    # Load additional CSV data files
    DEPARTURES_CSV = DATA_DIR / "departures.csv"
    EMPLOYEES_CSV = DATA_DIR / "employees.csv"
    TRAFFIC_CSV = DATA_DIR / "web_traffic.csv"
    NEWS_CSV = DATA_DIR / "news_events.csv"
    COMPANIES_CSV = DATA_DIR / "company_info.csv"
    
    # 1. EMPLOYEE SIGNALS (35%) - from departures.csv + employees.csv
    try:
        departures_df = pd.read_csv(DEPARTURES_CSV)
        employees_df = pd.read_csv(EMPLOYEES_CSV)
        
        # Check for C-Level departures
        departures = departures_df[departures_df['sme_id'] == sme_id]
        c_level_departures = len(departures[departures['seniority'] == 'C-Level'])
        
        # Check employee trend
        emp_data = employees_df[employees_df['sme_id'] == sme_id]
        emp_trend = emp_data.iloc[0]['trend'] if not emp_data.empty else 'stable'
        
        if c_level_departures >= 2:
            employee_score = 85
        elif c_level_departures == 1:
            employee_score = 70
        elif emp_trend == 'down':
            employee_score = 55
        elif emp_trend == 'up':
            employee_score = 15
        else:
            employee_score = 30
    except:
        # Fallback if files not found
        employee_score = 30
    
    # 2. WEB TRAFFIC SIGNALS (30%) - from web_traffic.csv
    try:
        traffic_df = pd.read_csv(TRAFFIC_CSV)
        traffic_data = traffic_df[traffic_df['sme_id'] == sme_id]
        
        if not traffic_data.empty:
            traffic_change = float(traffic_data.iloc[0]['sessions_change_qoq'])
            
            if traffic_change < -40:
                traffic_score = 95
            elif traffic_change < -25:
                traffic_score = 75
            elif traffic_change < -10:
                traffic_score = 50
            elif traffic_change > 10:
                traffic_score = 15
            else:
                traffic_score = 30
        else:
            traffic_score = 50
    except:
        traffic_score = 50
    
    # 3. NEWS SENTIMENT (20%) - from news_events.csv
    try:
        news_df = pd.read_csv(NEWS_CSV)
        news_data = news_df[news_df['sme_id'] == sme_id]
        
        if not news_data.empty:
            critical_events = len(news_data[news_data['severity'] == 'critical'])
            avg_sentiment = news_data['sentiment_score'].mean()
            
            if critical_events >= 2 or avg_sentiment < -0.7:
                news_score = 95
            elif critical_events == 1 or avg_sentiment < -0.4:
                news_score = 70
            elif avg_sentiment > 0.5:
                news_score = 15
            else:
                news_score = 30
        else:
            news_score = 30
    except:
        news_score = 30
    
    # 4. COMPANIES HOUSE FLAGS (15%) - from company_info.csv
    try:
        companies_df = pd.read_csv(COMPANIES_CSV)
        company_data = companies_df[companies_df['sme_id'] == sme_id]
        
        if not company_data.empty:
            director_changes = int(company_data.iloc[0]['director_changes_12m'])
            ccj_count = int(company_data.iloc[0]['ccj_count'])
            insolvency = bool(company_data.iloc[0]['insolvency_flag'])
            
            if insolvency:
                companies_house_score = 95
            elif ccj_count >= 3 or director_changes >= 3:
                companies_house_score = 80
            elif ccj_count >= 1 or director_changes >= 2:
                companies_house_score = 50
            else:
                companies_house_score = 20
        else:
            companies_house_score = 30
    except:
        companies_house_score = 30
    
    # Weighted composite
    alt_data_score = (
        employee_score * 0.35 +
        traffic_score * 0.30 +
        news_score * 0.20 +
        companies_house_score * 0.15
    )
    
    return alt_data_score