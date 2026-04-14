import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings, os

warnings.filterwarnings('ignore')
os.makedirs('figures', exist_ok=True)
os.makedirs('data', exist_ok=True)

plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
sns.set_style('whitegrid')

print('Libraries loaded.')

df = pd.read_csv('dismissal_events_with_tickers.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df['actual_year'] = df['date'].dt.year

print(f'Total dismissal events: {len(df)}')
print(f'Unique tickers: {df["ticker"].nunique()}')
print(f'Date range: {df["date"].min().date()} to {df["date"].max().date()}')


fig, axes = plt.subplots(1, 2, figsize=(16, 5))

yearly = df.groupby('actual_year').size()
axes[0].bar(yearly.index, yearly.values, color='#c0392b', alpha=0.85, edgecolor='white')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Number of Dismissals')
axes[0].set_title('CEO Dismissals by Year (Our Sample, n=405)')
axes[0].axvspan(2007.5, 2009.5, alpha=0.15, color='gray', label='2008 Crisis')
axes[0].axvspan(2000.5, 2002.5, alpha=0.15, color='blue', label='Dot-com Burst')
axes[0].legend()

monthly = df.groupby(df['date'].dt.month).size()
axes[1].bar(monthly.index, monthly.values, color='#2c3e50', alpha=0.85, edgecolor='white')
axes[1].set_xlabel('Month')
axes[1].set_ylabel('Number of Dismissals')
axes[1].set_title('CEO Dismissals by Month')
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], rotation=45)

plt.tight_layout()
plt.savefig('figures/eda_temporal_distribution.png', dpi=150, bbox_inches='tight')
plt.show()


code_labels = {3: 'Retired (Forced)', 4: 'Interim/Unknown'}
df['dep_label'] = df['dep_code'].map(code_labels)

fig, ax = plt.subplots(figsize=(10, 5))
dep_counts = df['dep_label'].value_counts()
colors = ['#c0392b' if 'Forced' in str(x) else '#7f8c8d' for x in dep_counts.index]
dep_counts.plot(kind='barh', ax=ax, color=colors, edgecolor='white')
ax.set_xlabel('Count')
ax.set_title('Departure Code Distribution (Among ceo_dismissal=1 Events)')
for i, v in enumerate(dep_counts.values):
    ax.text(v + 1, i, f'{v} ({v/len(df)*100:.1f}%)', va='center', fontsize=10)
plt.tight_layout()
plt.savefig('figures/eda_departure_codes.png', dpi=150, bbox_inches='tight')
plt.show()


repeats = df.groupby('ticker').agg(
    company=('coname', 'first'),
    dismissals=('ticker', 'size'),
).query('dismissals > 1').sort_values('dismissals', ascending=False)
print(f'\nCompanies with multiple CEO dismissals: {len(repeats)}')
print(repeats.head(15))

car_df = pd.read_csv('data/car_results.csv', parse_dates=['date'])

print(f'\nRaw CAR results loaded: {len(car_df)} events')
print(f'CAR [0,2] stats BEFORE cleaning:')
print(f'  Mean:   {car_df["car_0_2"].mean()*100:.2f}%')
print(f'  Median: {car_df["car_0_2"].median()*100:.2f}%')
print(f'  Min:    {car_df["car_0_2"].min()*100:.2f}%')
print(f'  Max:    {car_df["car_0_2"].max()*100:.2f}%')

for col in ['car_0_2', 'car_0_5', 'car_3_20', 'car_full']:
    car_df.loc[car_df[col].abs() > 1.0, col] = np.nan


car_df = car_df.dropna(subset=['car_0_2'])

print(f'\nAfter cleaning (|CAR| > 100% removed):')
print(f'  Remaining events: {len(car_df)}')
print(f'  CAR [0,2] Mean:   {car_df["car_0_2"].mean()*100:.3f}%')
print(f'  CAR [0,2] Median: {car_df["car_0_2"].median()*100:.3f}%')
print(f'  CAR [0,2] Std:    {car_df["car_0_2"].std()*100:.3f}%')
print(f'  CAR [0,2] Min:    {car_df["car_0_2"].min()*100:.3f}%')
print(f'  CAR [0,2] Max:    {car_df["car_0_2"].max()*100:.3f}%')


Q1 = car_df['car_0_2'].quantile(0.01)
Q99 = car_df['car_0_2'].quantile(0.99)
print(f'\n  1st percentile: {Q1*100:.2f}%')
print(f'  99th percentile: {Q99*100:.2f}%')


fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, col, title in zip(axes,
    ['car_0_2', 'car_0_5', 'car_full'],
    ['CAR [0, +2]', 'CAR [0, +5]', 'CAR [-5, +20]']):

    data = car_df[col].dropna() * 100
    ax.hist(data, bins=50, color='#c0392b', alpha=0.7, edgecolor='white')
    ax.axvline(0, color='black', linestyle='--', linewidth=1)
    ax.axvline(data.mean(), color='#2c3e50', linestyle='-', linewidth=2, label=f'Mean: {data.mean():.2f}%')
    ax.axvline(data.median(), color='#e67e22', linestyle='-.', linewidth=2, label=f'Median: {data.median():.2f}%')
    ax.set_xlabel('CAR (%)')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.legend(fontsize=9)

plt.suptitle('Distribution of Cumulative Abnormal Returns Around CEO Dismissals', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig('figures/car_distributions.png', dpi=150, bbox_inches='tight')
plt.show()

fig, ax = plt.subplots(figsize=(10, 6))
windows = {
    'Day 0-2': car_df['car_0_2'].mean() * 100,
    'Day 0-5': car_df['car_0_5'].dropna().mean() * 100,
    'Day 3-20': car_df['car_3_20'].dropna().mean() * 100,
    'Full [-5,+20]': car_df['car_full'].dropna().mean() * 100
}
colors = ['#c0392b' if v < 0 else '#27ae60' for v in windows.values()]
ax.bar(windows.keys(), windows.values(), color=colors, edgecolor='white', width=0.5)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel('Mean CAR (%)')
ax.set_title('Average Cumulative Abnormal Return by Event Window')
for i, (k, v) in enumerate(windows.items()):
    offset = 0.15 if v >= 0 else -0.25
    ax.text(i, v + offset, f'{v:.2f}%', ha='center', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/car_by_window.png', dpi=150, bbox_inches='tight')
plt.show()

yearly_car = car_df.groupby('year')['car_0_2'].agg(['mean','count','std']).reset_index()
yearly_car['se'] = yearly_car['std'] / np.sqrt(yearly_car['count'])

fig, ax = plt.subplots(figsize=(14, 6))
crisis_list = [2001, 2002, 2007, 2008, 2009]
colors = ['#c0392b' if y in crisis_list else '#2c3e50' for y in yearly_car['year']]
ax.bar(yearly_car['year'], yearly_car['mean']*100, yerr=yearly_car['se']*100*1.96,
       color=colors, alpha=0.85, edgecolor='white', capsize=3)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xlabel('Year')
ax.set_ylabel('Mean CAR [0,+2] (%)')
ax.set_title('Average Short-Term CAR by Year (Red = Crisis Years)')
plt.tight_layout()
plt.savefig('figures/car_by_year.png', dpi=150, bbox_inches='tight')
plt.show()

print('\n' + '='*60)
print('H1: CEO Dismissal → Significant Abnormal Return?')
print('='*60)

car_02 = car_df['car_0_2'].dropna()
t_stat, p_value = stats.ttest_1samp(car_02, 0)
cohens_d = car_02.mean() / car_02.std()
n = len(car_02)
se = car_02.std() / np.sqrt(n)

print(f'  N events:      {n}')
print(f'  Mean CAR[0,2]: {car_02.mean()*100:.3f}%')
print(f'  Std Dev:       {car_02.std()*100:.3f}%')
print(f'  t-statistic:   {t_stat:.4f}')
print(f'  p-value:       {p_value:.6f}')
print(f"  Cohen's d:     {cohens_d:.4f}")
print(f'  95% CI:        [{(car_02.mean()-1.96*se)*100:.3f}%, {(car_02.mean()+1.96*se)*100:.3f}%]')
h1_result = '✅ REJECT H0' if p_value < 0.05 else '❌ FAIL TO REJECT H0'
print(f'  Result: {h1_result}')

print('\n' + '='*60)
print('H2: Departure Code 3 (Forced Retirement) vs Code 4 (Interim)')
print('='*60)

code3 = car_df[car_df['dep_code'] == 3]['car_0_2'].dropna()
code4 = car_df[car_df['dep_code'] == 4]['car_0_2'].dropna()

if len(code4) >= 5:
    u_stat, p_val = stats.mannwhitneyu(code3, code4, alternative='two-sided')
    print(f'  Code 3 — N: {len(code3)}, Mean CAR: {code3.mean()*100:.3f}%, Median: {code3.median()*100:.3f}%')
    print(f'  Code 4 — N: {len(code4)}, Mean CAR: {code4.mean()*100:.3f}%, Median: {code4.median()*100:.3f}%')
    print(f'  Mann-Whitney U: {u_stat:.2f}')
    print(f'  p-value: {p_val:.6f}')
    h2_result = '✅ REJECT H0' if p_val < 0.05 else '❌ FAIL TO REJECT H0'
    print(f'  Result: {h2_result}')
else:
    print(f'  Code 4 too small (n={len(code4)}). Using early vs late period.')
    median_year = car_df['year'].median()
    early = car_df[car_df['year'] <= median_year]['car_0_2'].dropna()
    late = car_df[car_df['year'] > median_year]['car_0_2'].dropna()
    u_stat, p_val = stats.mannwhitneyu(early, late, alternative='two-sided')
    print(f'  Early (≤{int(median_year)}) — N: {len(early)}, Mean: {early.mean()*100:.3f}%')
    print(f'  Late  (>{int(median_year)}) — N: {len(late)}, Mean: {late.mean()*100:.3f}%')
    print(f'  Mann-Whitney U: {u_stat:.2f}, p-value: {p_val:.6f}')
    h2_result = '✅ REJECT H0' if p_val < 0.05 else '❌ FAIL TO REJECT H0'
    print(f'  Result: {h2_result}')

fig, ax = plt.subplots(figsize=(8, 6))
if len(code4) >= 5:
    plot_h2 = car_df[car_df['dep_code'].isin([3, 4])][['car_0_2','dep_code']].dropna().copy()
    plot_h2['group'] = plot_h2['dep_code'].map({3: 'Code 3\n(Forced Retirement)', 4: 'Code 4\n(Interim)'})
    plot_h2['car_pct'] = plot_h2['car_0_2'] * 100
    sns.boxplot(data=plot_h2, x='group', y='car_pct', palette=['#c0392b', '#e67e22'], ax=ax)
    ax.set_title(f'H2: Departure Code Comparison (p={p_val:.4f})')
else:
    plot_h2 = car_df[['car_0_2','year']].dropna().copy()
    plot_h2['group'] = plot_h2['year'].apply(lambda y: f'Early (≤{int(median_year)})' if y <= median_year else f'Late (>{int(median_year)})')
    plot_h2['car_pct'] = plot_h2['car_0_2'] * 100
    sns.boxplot(data=plot_h2, x='group', y='car_pct', palette=['#2c3e50', '#c0392b'], ax=ax)
    ax.set_title(f'H2: Early vs Late Period (p={p_val:.4f})')
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.set_ylabel('CAR [0,+2] (%)')
ax.set_xlabel('')
plt.tight_layout()
plt.savefig('figures/h2_departure_comparison.png', dpi=150, bbox_inches='tight')
plt.show()


print('\n' + '='*60)
print('H3: Mean Reversion — Initial Reaction vs Subsequent Drift')
print('='*60)

valid = car_df[['car_0_2', 'car_3_20']].dropna()
rho, p_val = stats.spearmanr(valid['car_0_2'], valid['car_3_20'])

print(f'  N events:   {len(valid)}')
print(f'  Spearman ρ: {rho:.4f}')
print(f'  p-value:    {p_val:.6f}')
if p_val < 0.05 and rho < 0:
    h3_result = '✅ REJECT H0 — Mean reversion'
elif p_val < 0.05 and rho > 0:
    h3_result = '⚠️ REJECT H0 — Momentum'
else:
    h3_result = '❌ FAIL TO REJECT H0 — No relationship'
print(f'  Result: {h3_result}')

fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(valid['car_0_2']*100, valid['car_3_20']*100, alpha=0.4, s=30, c='#c0392b', edgecolor='white')
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)
z = np.polyfit(valid['car_0_2'], valid['car_3_20'], 1)
x_line = np.linspace(valid['car_0_2'].min(), valid['car_0_2'].max(), 100)
ax.plot(x_line*100, np.poly1d(z)(x_line)*100, '--', color='#2c3e50', linewidth=2,
        label=f'ρ={rho:.3f}, p={p_val:.4f}')
ax.set_xlabel('Initial Reaction CAR [0,+2] (%)')
ax.set_ylabel('Subsequent Drift CAR [+3,+20] (%)')
ax.set_title('H3: Mean Reversion Test')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig('figures/h3_mean_reversion.png', dpi=150, bbox_inches='tight')
plt.show()

print('\n' + '='*60)
print('H4: Crisis Period (2007-2009) vs Normal Period')
print('='*60)

crisis_years = [2007, 2008, 2009]
crisis_car = car_df[car_df['year'].isin(crisis_years)]['car_0_2'].dropna()
normal_car = car_df[~car_df['year'].isin(crisis_years)]['car_0_2'].dropna()

u_stat, p_val = stats.mannwhitneyu(crisis_car, normal_car, alternative='less')

print(f'  Crisis  — N: {len(crisis_car)}, Mean: {crisis_car.mean()*100:.3f}%, Median: {crisis_car.median()*100:.3f}%')
print(f'  Normal  — N: {len(normal_car)}, Mean: {normal_car.mean()*100:.3f}%, Median: {normal_car.median()*100:.3f}%')
print(f'  Mann-Whitney U: {u_stat:.2f}')
print(f'  p-value (one-tailed): {p_val:.6f}')
h4_result = '✅ REJECT H0' if p_val < 0.05 else '❌ FAIL TO REJECT H0'
print(f'  Result: {h4_result}')

fig, ax = plt.subplots(figsize=(8, 6))
plot_h4 = car_df[['car_0_2', 'year']].dropna().copy()
plot_h4['period'] = plot_h4['year'].apply(lambda y: 'Crisis\n(2007-2009)' if y in crisis_years else 'Normal')
plot_h4['car_pct'] = plot_h4['car_0_2'] * 100
sns.boxplot(data=plot_h4, x='period', y='car_pct', palette=['#2c3e50', '#c0392b'], ax=ax,
            order=['Normal', 'Crisis\n(2007-2009)'])
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.set_ylabel('CAR [0,+2] (%)')
ax.set_xlabel('')
ax.set_title(f'H4: Crisis vs Normal — CAR Distribution (p={p_val:.4f})')
plt.tight_layout()
plt.savefig('figures/h4_crisis_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

print('\n' + '='*60)
print('H5: Trend in CEO Dismissal Frequency')
print('='*60)

yearly_counts = df.groupby('actual_year').size()
yearly_counts = yearly_counts[(yearly_counts.index >= 1997) & (yearly_counts.index <= 2018)]

rho_trend, p_trend = stats.spearmanr(yearly_counts.index, yearly_counts.values)
print(f'  Spearman ρ (year vs count): {rho_trend:.4f}')
print(f'  p-value: {p_trend:.6f}')
h5_result = f'✅ {"Increasing" if rho_trend > 0 else "Decreasing"} trend' if p_trend < 0.05 else '❌ No significant trend'
print(f'  Result: {h5_result}')

try:
    import pymannkendall as mk
    result = mk.original_test(yearly_counts.values)
    print(f'  Mann-Kendall S: {result.s}, p: {result.p:.6f}, trend: {result.trend}')
    print(f'  Sen slope: {result.slope:.3f} dismissals/year')
except ImportError:
    print('  (pymannkendall not installed — Spearman used as fallback)')

fig, ax = plt.subplots(figsize=(14, 5))
ax.bar(yearly_counts.index, yearly_counts.values, color='#c0392b', alpha=0.7, edgecolor='white')
z = np.polyfit(yearly_counts.index, yearly_counts.values, 1)
ax.plot(yearly_counts.index, np.poly1d(z)(yearly_counts.index), '--', color='#2c3e50', linewidth=2,
        label=f'Trend: {z[0]:+.2f}/year')
ax.set_xlabel('Year')
ax.set_ylabel('Number of CEO Dismissals')
ax.set_title('H5: CEO Dismissal Frequency Trend (1997-2018)')
ax.legend()
plt.tight_layout()
plt.savefig('figures/h5_dismissal_trend.png', dpi=150, bbox_inches='tight')
plt.show()

print('\n' + '='*70)
print('HYPOTHESIS TESTING — RESULTS SUMMARY')
print('='*70)
print(f'{"Hypothesis":<50} {"p-value":<12} {"Result"}')
print('-'*70)
print(f'{"H1: Dismissal → Negative CAR [0,+2]":<50} {p_value:<12.4f} {h1_result}')
print(f'{"H2: Dep. Code 3 vs 4 CAR difference":<50} {p_val:<12.4f} {h2_result}')


_, h3_p = stats.spearmanr(valid['car_0_2'], valid['car_3_20'])
print(f'{"H3: Mean Reversion (initial vs drift)":<50} {h3_p:<12.4f} {h3_result}')


crisis_car_h4 = car_df[car_df['year'].isin([2007,2008,2009])]['car_0_2'].dropna()
normal_car_h4 = car_df[~car_df['year'].isin([2007,2008,2009])]['car_0_2'].dropna()
_, h4_p = stats.mannwhitneyu(crisis_car_h4, normal_car_h4, alternative='less')
print(f'{"H4: Crisis (07-09) → More negative CAR":<50} {h4_p:<12.4f} {h4_result}')

print(f'{"H5: Increasing dismissal frequency trend":<50} {p_trend:<12.4f} {h5_result}')
print('-'*70)
print('\nAll figures saved to figures/ folder.')
print('Clean CAR data available in data/car_results.csv')
print('\n✅ Analysis complete.')