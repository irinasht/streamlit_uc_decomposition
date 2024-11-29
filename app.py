import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta


today = pd.to_datetime(datetime.today()).date()

df = pd.read_csv(f'uc_decomposition_{today}.csv')

df = df.loc[df.iteration.isin(['total_by_price_group','total'])]

test_or_not_test = st.selectbox("Which group do you want?", ('test','regular'))

if test_or_not_test == "test":
    dimensions = tuple(list(df.loc[df.price_group.str.contains('test')].price_group.unique()))
else:
    dimensions = tuple(list(df.loc[~df.price_group.str.contains('test')].price_group.unique()))


price_group = st.selectbox("Which dimension?", dimensions)

st.write("You selected:", price_group)


blank_df = df.query('price_group == @price_group').sort_values(['rank_period'])
blank_df['iteration'] = 'total_by_price_group'


ll1 = list(
    blank_df.query('iteration == "total_by_price_group"')
    .query(f'price_group == "{price_group}"')
    .set_index(["period"])["uc_perc"]
    .values
)
ll2 = list(
    blank_df.query('iteration == "total_by_price_group"')
    .query(f'price_group == "{price_group}"')
    .set_index("period")[["uc_perc"]]
    .apply(lambda x: np.round(x - x[0], 4))
    # .replace(0, np.nan)
    .values
)
ll2 = [x[0] for x in ll2]

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(17, 6))
axes[0].set_title(f"Динамика uc% в {price_group}")
axes[1].set_title("Разложение UC на вклады")


dinymics_by_total = (
    blank_df.query('iteration == "total_by_price_group"')
    .query(f'price_group == "{price_group}"')
    # .merge(periods, how="inner", left_on="period", right_on="periods_name")
    .set_index(["period_start"])[["infl", "cost_infl", "cost_mix", "mix", "discount"]]
)

dinymics_by_total["disc_growth"] = (
    dinymics_by_total["discount"] / dinymics_by_total["discount"][0] - 1
)


to_pic = (
    blank_df.query('iteration == "total_by_price_group"')
    .query(f'price_group == "{price_group}"')
    # .merge(periods, how="inner", left_on="period", right_on="periods_name")
    .set_index(["period_start"])
)


COLS = ["impact_infl", "impact_cost_infl", "impact_mix", "impact_discount"]

# blank_df.query('iteration=="total"').set_index("period")
# dinymics_by_total
to_pic[COLS].mul(100).plot(kind="bar", ax=axes[1], stacked=True)

# ax0twinx = axes[0].twinx()
to_pic["uc_perc_delta_relate_first_period"].mul(100).plot(
    ax=axes[1], marker="o", ms=10, color="black", linestyle="--"
)

to_pic.assign(uc_perc=lambda x: x["uc_perc"].mul(100))["uc_perc"].plot(
    ax=axes[0], marker="o", color="black"
)

for k, n, d in zip([*np.arange(1, len(ll1))], ll1[1:], ll2[1:]):
    axes[0].text(x=k * 0.95, y=n * 1.005 * 100, s=str(np.round(d * 100, 2)) + "%")


# Добавление подписей на каждом сегменте
for bar in axes[1].patches:
    # Получаем высоту и координаты каждой планки
    height = bar.get_height()
    # if height > 0:  # Подписываем только если высота больше нуля
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,  # X-координата
        bar.get_y() + height / 2,  # Y-координата
        f"{height:.2f}",  # Текст подписи
        ha="center",
        va="center",  # Выравнивание текста
    )
for i in [0, 1]:
    axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha="right")
axes[1].grid(linestyle="--", alpha=0.3)
axes[0].grid(linestyle="--", alpha=0.3)
axes[1].axhline(color="grey", linewidth=5, alpha=0.3)

axes[0].axhline(
    y=to_pic.assign(uc_perc=lambda x: x["uc_perc"].mul(100))["uc_perc"]
    .head(1)
    .values[0],
    color="black",
    linewidth=2,
    linestyle="--",
    
    alpha=0.3,
)
# axes[1].legend(['наша инфляция','инфляция себестоимости','микс','дисконт'])

axes[0].set_ylim(min(ll1) * 100 - 1 , max(ll1) * 100 + 1 )

st.pyplot(fig)
