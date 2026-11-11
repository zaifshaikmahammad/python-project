"""
Data Analysis and Visualization Module
Uses:
- Pandas for grouping expenses by month and category
- NumPy for summary statistics (sum, mean, median, standard deviation, min, max)
- Matplotlib for category-wise pie charts and month-wise bar charts
"""

import os
import io
import base64

# Configure Matplotlib writable cache directory for serverless environments (e.g. Vercel / AWS Lambda)
os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib')

import numpy as np
import pandas as pd
import matplotlib
# Headless backend for web server and serverless environment
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Modern aesthetic color palette for charts
CHART_COLORS = [
    '#3b82f6', # Blue
    '#10b981', # Emerald Green
    '#f59e0b', # Amber
    '#8b5cf6', # Violet
    '#ec4899', # Pink
    '#06b6d4', # Cyan
    '#f97316', # Orange
    '#6366f1', # Indigo
    '#14b8a6', # Teal
    '#84cc16'  # Lime
]

def fig_to_base64(fig):
    """Convert a Matplotlib figure to a Base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor=fig.get_facecolor(), transparent=False)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_b64}"

def generate_empty_chart_placeholder(message="No Expense Data Available"):
    """Generates an aesthetic placeholder chart image when no data is recorded."""
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#ffffff')
    ax.text(0.5, 0.5, message, horizontalalignment='center', verticalalignment='center',
            fontsize=13, color='#64748b', fontweight='500', transform=ax.transAxes)
    ax.axis('off')
    return fig_to_base64(fig)

def generate_category_pie_chart(category_summary_df):
    """
    Generates a modern category-wise pie/donut chart using Matplotlib.
    Features:
    - Donut chart styling with central white hole
    - Category percentage labels
    - Elegant legend
    """
    if category_summary_df.empty:
        return generate_empty_chart_placeholder("No Category Data to Display")
    
    fig, ax = plt.subplots(figsize=(6.5, 4.5), facecolor='#ffffff')
    
    categories = category_summary_df['category_name'].tolist()
    amounts = category_summary_df['total_amount'].tolist()
    colors = CHART_COLORS[:len(categories)]
    
    # Donut pie chart
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=None, # Use legend instead for cleaner look
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.75,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2)
    )
    
    # Customize percentage text inside the donut
    for autotext in autotexts:
        autotext.set_color('#1e293b')
        autotext.set_fontsize(9)
        autotext.set_weight('bold')
        
    ax.legend(
        wedges, 
        [f"{cat} ({pct:.1f}%)" for cat, pct in zip(categories, category_summary_df['percentage'])],
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        frameon=False,
        fontsize=9
    )
    
    ax.set_title("Category-Wise Expenditure Breakdown", fontsize=12, fontweight='bold', color='#1e293b', pad=15)
    plt.tight_layout()
    return fig_to_base64(fig)

def generate_monthly_bar_chart(monthly_summary_df):
    """
    Generates a month-wise bar chart using Matplotlib.
    Features:
    - Rounded-feel aesthetic bars
    - Currency value labels on top of each bar
    - Subtle horizontal gridlines
    """
    if monthly_summary_df.empty:
        return generate_empty_chart_placeholder("No Monthly Data to Display")
        
    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='#ffffff')
    
    months = monthly_summary_df['month_name'].tolist()
    totals = monthly_summary_df['total_amount'].tolist()
    
    # Modern gradient/accent bar styling
    bars = ax.bar(months, totals, color='#3b82f6', width=0.55, edgecolor='#2563eb', linewidth=1.2, zorder=3)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:,.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),  # 4 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='600', color='#1e293b')
        
    # Styling axes and grid
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#cbd5e1', zorder=0)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    ax.set_ylabel("Total Spent", fontsize=10, fontweight='600', color='#475569')
    ax.set_title("Month-Wise Spending Comparison", fontsize=12, fontweight='bold', color='#1e293b', pad=15)
    ax.tick_params(axis='x', colors='#334155', labelsize=10)
    ax.tick_params(axis='y', colors='#334155', labelsize=9)
    
    # Format Y axis numbers with commas
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    
    # Add extra headroom for bar annotations
    if totals:
        max_val = max(totals)
        ax.set_ylim(0, max_val * 1.15)
        
    plt.tight_layout()
    return fig_to_base64(fig)

def analyze_expenses(expenses_list):
    """
    Comprehensive Data Analysis pipeline.
    
    1. Loads expenses into Pandas DataFrame.
    2. Calculates summary statistics using NumPy (mean, median, std, min, max, total).
    3. Groups by Category to calculate sums, counts, and percentages.
    4. Identifies the highest-spending category.
    5. Groups by Month to calculate monthly expense totals.
    6. Groups by Payment Method for distribution.
    7. Generates Matplotlib Pie Chart and Bar Chart.
    """
    if not expenses_list:
        return {
            'has_data': False,
            'total_expenses': 0.0,
            'transaction_count': 0,
            'summary_stats': {
                'total': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'std_dev': 0.0,
                'min': 0.0,
                'max': 0.0,
                'daily_avg': 0.0
            },
            'highest_category': None,
            'category_breakdown': [],
            'monthly_totals': [],
            'payment_breakdown': [],
            'pie_chart': generate_empty_chart_placeholder("No Expenses Recorded"),
            'bar_chart': generate_empty_chart_placeholder("No Expenses Recorded")
        }
    
    # 1. Create Pandas DataFrame
    df = pd.DataFrame(expenses_list)
    df['expense_date'] = pd.to_datetime(df['expense_date'])
    df['amount'] = df['amount'].astype(float)
    df['month_year'] = df['expense_date'].dt.strftime('%Y-%m')
    df['month_name'] = df['expense_date'].dt.strftime('%b %Y')
    
    # 2. NumPy Statistical Calculations
    amounts = df['amount'].to_numpy()
    total_spent = float(np.sum(amounts))
    mean_spent = float(np.mean(amounts))
    median_spent = float(np.median(amounts))
    std_dev = float(np.std(amounts)) if len(amounts) > 1 else 0.0
    min_spent = float(np.min(amounts))
    max_spent = float(np.max(amounts))
    
    # Calculate daily average spend over active days
    unique_days = df['expense_date'].nunique()
    daily_avg = total_spent / unique_days if unique_days > 0 else 0.0
    
    # 3. Pandas Grouping: Category-Wise Spending & Percentages
    category_group = df.groupby('category_name').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    
    # Calculate percentages
    if total_spent > 0:
        category_group['percentage'] = (category_group['total_amount'] / total_spent) * 100
    else:
        category_group['percentage'] = 0.0
        
    category_group = category_group.sort_values(by='total_amount', ascending=False)
    
    # 4. Identify Highest-Spending Category
    highest_category = None
    if not category_group.empty:
        top_row = category_group.iloc[0]
        highest_category = {
            'name': top_row['category_name'],
            'amount': round(float(top_row['total_amount']), 2),
            'percentage': round(float(top_row['percentage']), 1),
            'count': int(top_row['transaction_count'])
        }
        
    # Convert category group to list of dictionaries
    category_breakdown = []
    for _, row in category_group.iterrows():
        category_breakdown.append({
            'category_name': row['category_name'],
            'total_amount': round(float(row['total_amount']), 2),
            'percentage': round(float(row['percentage']), 1),
            'count': int(row['transaction_count'])
        })
        
    # 5. Pandas Grouping: Month-Wise Expense Totals
    # Sort chronologically by month_year
    monthly_group = df.groupby(['month_year', 'month_name']).agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index().sort_values(by='month_year')
    
    monthly_totals = []
    for _, row in monthly_group.iterrows():
        monthly_totals.append({
            'month_year': row['month_year'],
            'month_name': row['month_name'],
            'total_amount': round(float(row['total_amount']), 2),
            'count': int(row['transaction_count'])
        })
        
    # 6. Payment Method Breakdown
    payment_group = df.groupby('payment_method').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index().sort_values(by='total_amount', ascending=False)
    
    payment_breakdown = []
    for _, row in payment_group.iterrows():
        pct = (row['total_amount'] / total_spent * 100) if total_spent > 0 else 0
        payment_breakdown.append({
            'method': row['payment_method'],
            'total_amount': round(float(row['total_amount']), 2),
            'percentage': round(pct, 1),
            'count': int(row['transaction_count'])
        })
        
    # 7. Generate Matplotlib Charts
    pie_chart_b64 = generate_category_pie_chart(category_group)
    bar_chart_b64 = generate_monthly_bar_chart(monthly_group)
    
    return {
        'has_data': True,
        'total_expenses': round(total_spent, 2),
        'transaction_count': len(df),
        'summary_stats': {
            'total': round(total_spent, 2),
            'mean': round(mean_spent, 2),
            'median': round(median_spent, 2),
            'std_dev': round(std_dev, 2),
            'min': round(min_spent, 2),
            'max': round(max_spent, 2),
            'daily_avg': round(daily_avg, 2),
            'unique_days': unique_days
        },
        'highest_category': highest_category,
        'category_breakdown': category_breakdown,
        'monthly_totals': monthly_totals,
        'payment_breakdown': payment_breakdown,
        'pie_chart': pie_chart_b64,
        'bar_chart': bar_chart_b64
    }

def generate_monthly_report_analysis(expenses_list, target_month_str):
    """
    Dedicated generator for Monthly Expense Reports.
    target_month_str format: 'YYYY-MM' (e.g. '2026-10')
    """
    if not expenses_list:
        return None
        
    df = pd.DataFrame(expenses_list)
    df['expense_date'] = pd.to_datetime(df['expense_date'])
    df['amount'] = df['amount'].astype(float)
    df['month_year'] = df['expense_date'].dt.strftime('%Y-%m')
    df['month_name'] = df['expense_date'].dt.strftime('%B %Y')
    
    # Filter for the target month
    m_df = df[df['month_year'] == target_month_str].copy()
    if m_df.empty:
        return None
        
    month_name = m_df['month_name'].iloc[0]
    total_spent = float(np.sum(m_df['amount'].to_numpy()))
    transaction_count = len(m_df)
    unique_active_days = m_df['expense_date'].nunique()
    daily_average = total_spent / unique_active_days if unique_active_days > 0 else 0.0
    
    # Category Breakdown for this month
    cat_df = m_df.groupby('category_name').agg(
        total_amount=('amount', 'sum'),
        transaction_count=('amount', 'count')
    ).reset_index()
    cat_df['percentage'] = (cat_df['total_amount'] / total_spent * 100) if total_spent > 0 else 0
    cat_df = cat_df.sort_values(by='total_amount', ascending=False)
    
    highest_cat = None
    if not cat_df.empty:
        top_row = cat_df.iloc[0]
        highest_cat = {
            'name': top_row['category_name'],
            'amount': round(float(top_row['total_amount']), 2),
            'percentage': round(float(top_row['percentage']), 1)
        }
        
    category_summary = []
    for _, row in cat_df.iterrows():
        category_summary.append({
            'category_name': row['category_name'],
            'total_amount': round(float(row['total_amount']), 2),
            'percentage': round(float(row['percentage']), 1),
            'count': int(row['transaction_count'])
        })
        
    # Individual transactions sorted by date descending
    transactions = m_df.sort_values(by='expense_date', ascending=False).to_dict('records')
    for tx in transactions:
        tx['expense_date'] = tx['expense_date'].strftime('%Y-%m-%d')
        tx['amount'] = round(float(tx['amount']), 2)
        
    # Monthly mini-pie chart
    mini_pie = generate_category_pie_chart(cat_df)
    
    return {
        'month_year': target_month_str,
        'month_name': month_name,
        'total_spent': round(total_spent, 2),
        'transaction_count': transaction_count,
        'unique_days': unique_active_days,
        'daily_average': round(daily_average, 2),
        'highest_category': highest_cat,
        'category_summary': category_summary,
        'transactions': transactions,
        'chart': mini_pie
    }
