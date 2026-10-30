    ].copy()

    facility_rank = (
        ranking
        .groupby(
            COL_FAC,
            as_index=False
        )[COL_GEN]
        .sum()
        .sort_values(
            COL_GEN,
            ascending=False
        )
    )

    max_n = min(
        20,
        len(facility_rank)
    )

    top_n = st.slider(
        "표시할 발전설비 수",
        min_value=5,
        max_value=max_n,
        value=min(10, max_n)
    )

    top_facilities = (
        facility_rank
        .head(top_n)
        .sort_values(COL_GEN)
    )

    fig = px.bar(
        top_facilities,
        x=COL_GEN,
        y=COL_FAC,
        orientation="h",
        labels={
            COL_GEN: "총 발전량(kWh)",
            COL_FAC: "발전설비"
        },
        title=f"발전량 상위 {top_n}개 설비"
    )

    fig.update_layout(
        plot_bgcolor="#F8FFFB",
        paper_bgcolor="#FFFFFF"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📋 전체 발전설비 순위")

    ranking_table = facility_rank.copy()

    ranking_table.insert(
        0,
        "순위",
        range(
            1,
            len(ranking_table) + 1
        )
    )

    ranking_table = ranking_table.rename(
        columns={
            COL_GEN: "총 발전량(kWh)"
        }
    )

    st.dataframe(
        ranking_table,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# 지역별 발전량
# ============================================================
elif st.session_state.page == "region":

    st.title("🗺️ 지역별 발전량")

    st.caption(
        "발전설비 이름을 기준으로 지역을 "
        "추정하여 발전량을 비교합니다."
    )

    # HTML 대신 st.info 사용
    # → <div> 같은 코드가 화면에 표시되지 않음
    st.info(
        "💡 별도의 지역 컬럼이 없어 "
        "발전설비 이름의 앞부분을 기준으로 "
        "지역을 추정했습니다."
    )

    min_date = df[COL_DATE].min().date()
    max_date = df[COL_DATE].max().date()

    period = st.date_input(
        "비교 기간",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if (
        not isinstance(period, (tuple, list))
        or len(period) != 2
    ):

        st.warning(
            "기간의 시작일과 종료일을 모두 선택해 주세요."
        )

        st.stop()

    start = pd.to_datetime(period[0])
    end = pd.to_datetime(period[1])

    region_data = df[
        (df[COL_DATE] >= start)
        &
        (df[COL_DATE] <= end)
    ].copy()

    region_data["지역"] = (
        region_data[COL_FAC]
        .apply(get_region)
    )

    region_rank = (
        region_data
        .groupby(
            "지역",
            as_index=False
        )[COL_GEN]
        .sum()
        .sort_values(
            COL_GEN,
            ascending=False
        )
    )

    fig = px.bar(
        region_rank,
        x="지역",
        y=COL_GEN,
        labels={
            "지역": "추정 지역",
            COL_GEN: "총 발전량(kWh)"
        },
        title="지역별 총 발전량"
    )

    fig.update_layout(
        plot_bgcolor="#F8FFFB",
        paper_bgcolor="#FFFFFF"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📋 지역별 발전량")

    region_table = region_rank.copy()

    region_table["발전량(MWh)"] = (
        region_table[COL_GEN] / 1000
    ).round(1)

    region_table = region_table[
        [
            "지역",
            "발전량(MWh)"
        ]
    ]

    st.dataframe(
        region_table,
        hide_index=True,
        use_container_width=True
    )
