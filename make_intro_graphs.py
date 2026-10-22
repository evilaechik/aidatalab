import matplotlib.pyplot as plt
from pathlib import Path

out = Path('intro_graphs')
out.mkdir(exist_ok=True)
navy, blue, peach, teal, grey = '#16324F', '#2F80ED', '#F2994A', '#27AE60', '#667085'
plt.rcParams.update({'font.family':'DejaVu Sans','axes.titleweight':'bold','axes.titlesize':18,'axes.labelsize':11})

fig, ax = plt.subplots(figsize=(8.4,5.1), facecolor='white')
bars = ax.bar(['Atlanta','Charlotte','Nashville'], [1.2,1.9,.3], color=[blue,peach,teal], width=.58)
ax.set_title('Atlanta is adding jobs—Charlotte grew faster', loc='left', color=navy, pad=18)
ax.set_ylabel('Employment growth (%)'); ax.set_ylim(0,2.25); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
ax.spines[['top','right','left']].set_visible(False); ax.spines['bottom'].set_color('#D0D5DD'); ax.tick_params(left=False)
for b,v,n in zip(bars,[1.2,1.9,.3],[37000,26200,3900]):
    ax.text(b.get_x()+b.get_width()/2,v+.055,f'{v:.1f}% | {n:,} jobs',ha='center',fontsize=10,color=navy,weight='bold')
fig.text(.01,.015,'Year-over-year, June 2023 to June 2024. Source: U.S. Bureau of Labor Statistics.',fontsize=8.5,color=grey)
fig.tight_layout(rect=[0,.05,1,1]); fig.savefig(out/'metro_job_growth.png',dpi=180,bbox_inches='tight'); plt.close(fig)

fig, ax = plt.subplots(figsize=(8.4,4.7),facecolor='white')
bars = ax.barh(['Fortune 500 companies','Fortune 1000 companies'],[17,37],color=[blue,navy],height=.55)
ax.invert_yaxis(); ax.set_xlim(0,44); ax.set_title('Metro Atlanta has a strong corporate base',loc='left',color=navy,pad=18)
ax.set_xlabel('Number headquartered in metro Atlanta'); ax.grid(axis='x',alpha=.2); ax.set_axisbelow(True)
ax.spines[['top','right','left']].set_visible(False); ax.spines['bottom'].set_color('#D0D5DD'); ax.tick_params(left=False)
for b,v in zip(bars,[17,37]): ax.text(v+.7,b.get_y()+b.get_height()/2,str(v),va='center',fontsize=13,weight='bold',color=navy)
fig.text(.01,.015,'Source: Georgia Department of Economic Development regional profile.',fontsize=8.5,color=grey)
fig.tight_layout(rect=[0,.05,1,1]); fig.savefig(out/'corporate_presence.png',dpi=180,bbox_inches='tight'); plt.close(fig)

fig, ax = plt.subplots(figsize=(8.4,4.6),facecolor='white')
ax.barh(['Hartsfield-Jackson (FY 2024)'],[107.5],color=peach,height=.48); ax.set_xlim(0,125)
ax.set_title('Atlanta’s airport connects it to a global market',loc='left',color=navy,pad=18)
ax.set_xlabel('Passengers served (millions)'); ax.grid(axis='x',alpha=.2); ax.set_axisbelow(True)
ax.spines[['top','right','left']].set_visible(False); ax.spines['bottom'].set_color('#D0D5DD'); ax.tick_params(left=False)
ax.text(109,0,'107.5M',va='center',fontsize=14,weight='bold',color=navy)
fig.text(.01,.015,'Fiscal year 2024. Source: Hartsfield-Jackson annual disclosure.',fontsize=8.5,color=grey)
fig.tight_layout(rect=[0,.05,1,1]); fig.savefig(out/'airport_passengers.png',dpi=180,bbox_inches='tight'); plt.close(fig)
