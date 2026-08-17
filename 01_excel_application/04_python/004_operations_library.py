##############################
## OPERATION == NO CHANGE ####
##############################

## No change means case is included with no changes to the profile

def apply_nochange(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """Return an independent copy of the data without transformation."""
    return df.copy()

##############################
## OPERATION == DELAY ########
##############################

## Apply cash-cost penalty is called into the delay operation function if user inputs the optional parameters penalty_amount and penalty_year. 
## The function will create a new row for each impacted metric if the penalty year does not exist in the delayed profile.

def apply_cash_cost_penalty(
    df,
    penalty_amount=None,
    penalty_year=None
):
    """
    Apply a one-off cash-cost penalty.

    Where the penalty year does not exist in the delayed profile,
    create a new penalty-only row for each impacted metric.

    Parameters
    ----------
    df : pd.DataFrame
        Delayed financial profile.

    penalty_amount : float, optional
        Positive penalty amount in the model's reporting units.

    penalty_year : int, optional
        Absolute calendar year in which the penalty is booked.
    """

    result = df.copy()

    # No penalty requested
    if pd.isna(penalty_amount) or float(penalty_amount) == 0:
        return result

    # No valid booking year supplied
    if pd.isna(penalty_year) or int(penalty_year) == 0:
        return result

    penalty_year = int(penalty_year)

    # Do not create rows outside the model horizon
    if penalty_year < YEAR_MIN or penalty_year > YEAR_MAX:
        return result

    penalty_delta = -abs(float(penalty_amount))

    impacted_metrics = [
        "Total Cash Costs",
        "EBITDA",
        "Underlying RCOP",
        "Operating Cashflow",
        "Pre Tax Cash Flow"
    ]

    new_rows = []

    for metric in impacted_metrics:

        metric_mask = result["Metric"] == metric
        metric_rows = result.loc[metric_mask]

        # Each impacted metric should exist somewhere in the case profile
        if metric_rows.empty:
            raise ValueError(
                f"Metric '{metric}' does not exist in the case profile."
            )

        penalty_year_mask = (
            metric_mask
            & (result["Year"] == penalty_year)
        )

        matching_rows = int(penalty_year_mask.sum())

        if matching_rows > 1:
            raise ValueError(
                f"Expected no more than one '{metric}' row for "
                f"{penalty_year}, but found {matching_rows}."
            )

        # Create a penalty-only row where the year does not already exist
        if matching_rows == 0:
            new_row = metric_rows.iloc[[0]].copy()

            new_row["Year"] = penalty_year
            new_row["Value"] = 0.0

            new_rows.append(new_row)

    # Add any missing penalty-year rows
    if new_rows:
        result = pd.concat(
            [result, *new_rows],
            ignore_index=True
        )

    # Apply the penalty to all impacted metrics
    impact_mask = (
        result["Metric"].isin(impacted_metrics)
        & (result["Year"] == penalty_year)
    )

    result.loc[impact_mask, "Value"] = (
        result.loc[impact_mask, "Value"].fillna(0)
        + penalty_delta
    )

    return result

## Delay operation main code block is below. It calls the apply_cash_cost_penalty function
## It delays the profile by the number of years specified in param1 and applies a one-off cash-cost penalty if requested.

def apply_delay(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Delay the profile and optionally apply a one-off Cash Costs penalty.

    Parameters
    ----------
    param1 : int
        Positive whole number of years by which to delay the profile.

    param2 : float, optional
        Cash Costs penalty amount. Enter as a positive value.

    param3 : int, optional
        Absolute calendar year in which the penalty is booked.

    param4, param5
        Reserved for future use.
    """

    result = df.copy()

    delay_years = float(param1) if pd.notna(param1) else 0

    if delay_years < 0:
        raise ValueError(
            "Delay years must be zero or a positive whole number."
        )

    if not delay_years.is_integer():
        raise ValueError(
            "Delay years must be entered as a whole number."
        )

    delay_years = int(delay_years)

    # Shift the complete profile
    result["Year"] = result["Year"] + delay_years

    # Remove values shifted beyond the model horizon
    result = result.loc[
        result["Year"] <= YEAR_MAX
    ].copy()

    # Apply penalty to the shifted profile
    result = apply_cash_cost_penalty(
        df=result,
        penalty_amount=param2,
        penalty_year=param3
    )

    return result

##############################
## OPERATION == ACCELERATION #
##############################

## This helper function is called into the acceleration operation function if user inputs the optional parameters capex_amount and capex_year.

def apply_acceleration_capex(
    df,
    capex_amount=None,
    capex_year=None
):
    """
    Apply a one-off incremental CAPEX requirement associated with
    accelerating a case.

    Where the CAPEX year does not exist in the accelerated profile,
    create a new CAPEX-only row for each impacted metric.

    Parameters
    ----------
    df : pd.DataFrame
        Accelerated financial profile.

    capex_amount : float, optional
        Positive incremental CAPEX amount in the model's reporting units.

    capex_year : int, optional
        Absolute calendar year in which the additional CAPEX is booked.

    Notes
    -----
    Cash Capex and Pre Tax Cash Flow use the account sign convention.
    A positive input is therefore converted to a negative financial delta.
    """

    result = df.copy()

    # No incremental CAPEX requested
    if pd.isna(capex_amount) or float(capex_amount) == 0:
        return result

    # No valid booking year supplied
    if pd.isna(capex_year) or int(capex_year) == 0:
        return result

    capex_year = int(capex_year)

    # Do not create rows outside the model horizon
    if capex_year < YEAR_MIN or capex_year > YEAR_MAX:
        return result

    capex_delta = -abs(float(capex_amount))

    impacted_metrics = [
        "Cash Capex",
        "Pre Tax Cash Flow"
    ]

    new_rows = []

    for metric in impacted_metrics:

        metric_mask = result["Metric"] == metric
        metric_rows = result.loc[metric_mask]

        # Each impacted metric should exist somewhere in the case profile
        if metric_rows.empty:
            raise ValueError(
                f"Metric '{metric}' does not exist in the case profile."
            )

        capex_year_mask = (
            metric_mask
            & (result["Year"] == capex_year)
        )

        matching_rows = int(capex_year_mask.sum())

        if matching_rows > 1:
            raise ValueError(
                f"Expected no more than one '{metric}' row for "
                f"{capex_year}, but found {matching_rows}."
            )

        # Create a CAPEX-only row if the year does not already exist
        if matching_rows == 0:
            new_row = metric_rows.iloc[[0]].copy()

            new_row["Year"] = capex_year
            new_row["Value"] = 0.0

            new_rows.append(new_row)

    # Add missing CAPEX-year rows
    if new_rows:
        result = pd.concat(
            [result, *new_rows],
            ignore_index=True
        )

    # Apply the additional CAPEX to all impacted metrics
    impact_mask = (
        result["Metric"].isin(impacted_metrics)
        & (result["Year"] == capex_year)
    )

    result.loc[impact_mask, "Value"] = (
        result.loc[impact_mask, "Value"].fillna(0)
        + capex_delta
    )

    return result

## This function is the main code block for the acceleration operation.
## It shifts the profile earlier by the number of years specified in param1 and applies a one-off incremental CAPEX if requested.

def apply_accelerate(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Accelerate the profile and optionally apply one-off incremental CAPEX.

    Parameters
    ----------
    param1 : int
        Positive whole number of years by which to accelerate the profile.

    param2 : float, optional
        Additional CAPEX required to accelerate the case.
        Enter as a positive value.

    param3 : int, optional
        Absolute calendar year in which the additional CAPEX is booked.

    param4, param5
        Reserved for future use.
    """

    result = df.copy()

    accelerate_years = float(param1) if pd.notna(param1) else 0

    if accelerate_years < 0:
        raise ValueError(
            "Acceleration years must be zero or a positive whole number."
        )

    if not accelerate_years.is_integer():
        raise ValueError(
            "Acceleration years must be entered as a whole number."
        )

    accelerate_years = int(accelerate_years)

    # Shift the complete profile earlier
    result["Year"] = result["Year"] - accelerate_years

    # Remove values accelerated before the model horizon
    result = result.loc[
        result["Year"] >= YEAR_MIN
    ].copy()

    # Apply incremental acceleration CAPEX
    result = apply_acceleration_capex(
        df=result,
        capex_amount=param2,
        capex_year=param3
    )

    return result

##############################
## OPERATION == FARM-IN  #####
##############################

## This helper function is called into the farm-in operation function if user inputs the optional parameters payment_amount and payment_year.

def apply_farm_in_payment(
    df,
    payment_amount=None,
    payment_year=None,
    template_df=None
):
    """
    Apply a one-off payment associated with a farm-in transaction.

    If an impacted metric does not exist in the payment year,
    create a new payment-only row using the original case profile
    as the metadata template.

    Parameters
    ----------
    df : pd.DataFrame
        Increased financial and operational profile.

    payment_amount : float, optional
        Positive transaction payment in the model's reporting units.

    payment_year : int, optional
        Absolute calendar year in which the payment is made.

    template_df : pd.DataFrame, optional
        Original case profile used to provide case metadata.
    """

    result = df.copy()

    if pd.isna(payment_amount) or float(payment_amount) == 0:
        return result

    if pd.isna(payment_year) or int(payment_year) == 0:
        return result

    payment_year = int(payment_year)

    if payment_year < YEAR_MIN or payment_year > YEAR_MAX:
        return result

    payment_delta = -abs(float(payment_amount))

    impacted_metrics = [
        "Cash Capex",
        "Pre Tax Cash Flow"
    ]

    template = (
        template_df.copy()
        if template_df is not None
        else result.copy()
    )

    if template.empty:
        raise ValueError(
            "Cannot create farm-in payment rows because no case "
            "profile is available as a metadata template."
        )

    new_rows = []

    for metric in impacted_metrics:

        payment_year_mask = (
            (result["Metric"] == metric)
            & (result["Year"] == payment_year)
        )

        matching_rows = int(payment_year_mask.sum())

        if matching_rows > 1:
            raise ValueError(
                f"Expected no more than one '{metric}' row for "
                f"{payment_year}, but found {matching_rows}."
            )

        if matching_rows == 0:

            metric_template = template.loc[
                template["Metric"] == metric
            ]

            if not metric_template.empty:
                new_row = metric_template.iloc[[0]].copy()
            else:
                new_row = template.iloc[[0]].copy()

            new_row["Metric"] = metric
            new_row["Year"] = payment_year
            new_row["Value"] = 0.0

            new_rows.append(new_row)

    if new_rows:
        result = pd.concat(
            [result, *new_rows],
            ignore_index=True
        )

    impact_mask = (
        result["Metric"].isin(impacted_metrics)
        & (result["Year"] == payment_year)
    )

    result.loc[impact_mask, "Value"] = (
        result.loc[impact_mask, "Value"].fillna(0)
        + payment_delta
    )

    return result

## This is the main function for farm-in operations. 
## It increases the profile by the fraction specified in param1 and applies a one-off farm-in payment if requested.
## It applies the one-off payment using the helper function apply_farm_in_payment.

def apply_increase(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Increase the ownership-related profile and optionally apply
    a one-off farm-in payment.

    Parameters
    ----------
    param1 : float
        Fractional increase in the existing profile.

        Examples:
        0.25 = 25% increase
        1.00 = 100% increase, meaning the profile doubles

    param2 : int, optional
        First year in which the increase applies.
        Defaults to the first year in the profile.

    param3 : int, optional
        Final year in which the increase applies.
        Defaults to the final year in the profile.

    param4 : float, optional
        One-off farm-in payment. Enter as a positive amount.

    param5 : int, optional
        Absolute calendar year in which the payment is made.
    """

    original_profile = df.copy()
    result = df.copy()

    if pd.isna(param1):
        return result

    increase_fraction = float(param1)

    if increase_fraction < 0:
        raise ValueError(
            "Farm-in percentage cannot be negative."
        )

    start_year = (
        int(param2)
        if pd.notna(param2) and param2 != 0
        else int(result["Year"].min())
    )

    end_year = (
        int(param3)
        if pd.notna(param3) and param3 != 0
        else int(result["Year"].max())
    )

    if start_year > end_year:
        raise ValueError(
            "Farm-in start year cannot be after the end year."
        )

    increase_mask = (
        (result["Year"] >= start_year)
        & (result["Year"] <= end_year)
    )

    increase_factor = 1 + increase_fraction

    result.loc[increase_mask, "Value"] = (
        result.loc[increase_mask, "Value"]
        * increase_factor
    )

    result = apply_farm_in_payment(
        df=result,
        payment_amount=param4,
        payment_year=param5,
        template_df=original_profile
    )

    return result

##############################
## OPERATION == FARM-DOWN ####
##############################

## This helper function supports the main function apply_dilution, which reduces the profile by the fraction specified in param1
## and applies a one-off disposal proceeds payment if requested.

def apply_dilution_proceeds(
    df,
    proceeds_amount=None,
    proceeds_year=None,
    template_df=None
):
    """
    Apply one-off proceeds received from a farm-down or disposal.

    If an impacted metric does not exist in the proceeds year,
    create a new proceeds-only row using the original case profile
    as the metadata template.

    Parameters
    ----------
    df : pd.DataFrame
        Diluted financial profile.

    proceeds_amount : float, optional
        Positive disposal proceeds in the model's reporting units.

    proceeds_year : int, optional
        Absolute calendar year in which proceeds are received.

    template_df : pd.DataFrame, optional
        Original undiluted case profile used to supply case metadata.
        This is particularly important where a 100% disposal removes
        all underlying profile rows.
    """

    result = df.copy()

    # No proceeds requested
    if pd.isna(proceeds_amount) or float(proceeds_amount) == 0:
        return result

    # No valid proceeds year supplied
    if pd.isna(proceeds_year) or int(proceeds_year) == 0:
        return result

    proceeds_year = int(proceeds_year)

    # Do not create rows outside the model horizon
    if proceeds_year < YEAR_MIN or proceeds_year > YEAR_MAX:
        return result

    proceeds_delta = abs(float(proceeds_amount))

    impacted_metrics = [
        "Cash Flow from Sale of Operations",
        "Pre Tax Cash Flow"
    ]

    # Prefer the original profile as the source of case metadata
    template = (
        template_df.copy()
        if template_df is not None
        else result.copy()
    )

    if template.empty:
        raise ValueError(
            "Cannot create disposal proceeds rows because no case "
            "profile is available as a metadata template."
        )

    new_rows = []

    for metric in impacted_metrics:

        proceeds_year_mask = (
            (result["Metric"] == metric)
            & (result["Year"] == proceeds_year)
        )

        matching_rows = int(proceeds_year_mask.sum())

        if matching_rows > 1:
            raise ValueError(
                f"Expected no more than one '{metric}' row for "
                f"{proceeds_year}, but found {matching_rows}."
            )

        # Create the metric-year row where it does not already exist
        if matching_rows == 0:

            # Use an existing row for the same metric where possible
            metric_template = template.loc[
                template["Metric"] == metric
            ]

            if not metric_template.empty:
                new_row = metric_template.iloc[[0]].copy()
            else:
                # The metric does not exist anywhere in the case.
                # Use any case row to preserve ID, Case and dimensions.
                new_row = template.iloc[[0]].copy()

            new_row["Metric"] = metric
            new_row["Year"] = proceeds_year
            new_row["Value"] = 0.0

            new_rows.append(new_row)

    # Add newly created proceeds rows
    if new_rows:
        result = pd.concat(
            [result, *new_rows],
            ignore_index=True
        )

    # Apply positive proceeds to both cash-flow metrics
    impact_mask = (
        result["Metric"].isin(impacted_metrics)
        & (result["Year"] == proceeds_year)
    )

    result.loc[impact_mask, "Value"] = (
        result.loc[impact_mask, "Value"].fillna(0)
        + proceeds_delta
    )

    return result


## This function is the main code block for the dilution operation.
## It reduces the profile by the fraction specified in param1 and applies a one-off disposal proceeds payment if requested.
## It users the helper function apply_dilution_proceeds to apply the proceeds payment.

def apply_dilution(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Reduce ownership-related profile values and optionally apply
    one-off disposal proceeds.

    Parameters
    ----------
    param1 : float
        Fraction of the interest disposed.

        Examples:
        0.25 = 25% dilution
        1.00 = 100% disposal

    param2 : int, optional
        First year in which the dilution applies.
        Defaults to the first year in the profile.

    param3 : int, optional
        Final year in which the dilution applies.
        Defaults to the final year in the profile.

    param4 : float, optional
        Disposal proceeds received. Enter as a positive value.

    param5 : int, optional
        Absolute calendar year in which proceeds are received.
    """

    original_profile = df.copy()
    result = df.copy()

    if pd.isna(param1):
        return result

    dilution_fraction = float(param1)

    if dilution_fraction < 0 or dilution_fraction > 1:
        raise ValueError(
            "Dilution percentage must be between 0 and 1 inclusive."
        )

    start_year = (
        int(param2)
        if pd.notna(param2) and param2 != 0
        else int(result["Year"].min())
    )

    end_year = (
        int(param3)
        if pd.notna(param3) and param3 != 0
        else int(result["Year"].max())
    )

    if start_year > end_year:
        raise ValueError(
            "Dilution start year cannot be after the end year."
        )

    dilution_mask = (
        (result["Year"] >= start_year)
        & (result["Year"] <= end_year)
    )

    if dilution_fraction == 1:

        # Full disposal: remove the underlying profile for the period
        result = result.loc[
            ~dilution_mask
        ].copy()

    else:

        # Partial disposal: retain the remaining economic interest
        remaining_interest = 1 - dilution_fraction

        result.loc[dilution_mask, "Value"] = (
            result.loc[dilution_mask, "Value"]
            * remaining_interest
        )

    # Add one-off proceeds after scaling or removing the profile
    result = apply_dilution_proceeds(
        df=result,
        proceeds_amount=param4,
        proceeds_year=param5,
        template_df=original_profile
    )

    return result

##############################
## OPERATION == TRUNCATE #####
##############################

## These two similar functions are used to truncate the profile either before or after a specified year.
## This could represent early cessation of production (truncate after) or a later start to production / activity (truncate before).

#### BEFORE ####

def apply_truncate_before(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Remove all profile records before the specified year.

    Parameters
    ----------
    param1 : int
        First year to retain.

    param2, param3, param4, param5
        Reserved for future use.
    """

    result = df.copy()

    if pd.isna(param1):
        return result

    truncate_year = int(param1)

    return result.loc[
        result["Year"] >= truncate_year
    ].copy()

#### AFTER ####

def apply_truncate_after(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Remove all profile records after the specified year.

    Parameters
    ----------
    param1 : int
        Final year to retain.

    param2, param3, param4, param5
        Reserved for future use.
    """

    result = df.copy()

    if pd.isna(param1):
        return result

    truncate_year = int(param1)

    return result.loc[
        result["Year"] <= truncate_year
    ].copy()


##############################
## OPERATION == Δ PRODUCTION #
##############################

## This function is the main code block for the proportional production adjustment operation.
## It works by scaling all production metrics and selected financial drivers by the production change.
## It assumes that the production change is expressed as a decimal fraction, e.g. 0.10 = 10% increase, -0.10 = 10% reduction, -1.00 = 100% reduction.
## It assumes that financial drivers are linearly correlated with production, and that the resulting driver deltas are then propagated to EBITDA, Underlying RCOP, Operating Cashflow and Pre Tax Cash Flow.

def apply_ProdnAdj(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Apply a proportional production adjustment.

    All production metrics and selected financial driver metrics are
    scaled by the production change. The resulting driver deltas are
    then propagated to EBITDA, Underlying RCOP, Operating Cashflow
    and Pre Tax Cash Flow.

    Parameters
    ----------
    param1 : float
        Production adjustment expressed as a decimal fraction.

        Examples:
         0.10 = 10% increase
        -0.10 = 10% reduction
        -1.00 = 100% reduction

    param2 : int, optional
        First year in which the adjustment applies.
        Defaults to YEAR_MIN.

    param3 : int, optional
        Final year in which the adjustment applies.
        Defaults to YEAR_MAX.

    param4, param5
        Reserved for future use.
    """

    result = df.copy()

    if pd.isna(param1):
        return result

    production_change = float(param1)

    if production_change < -1:
        raise ValueError(
            "Production reduction cannot be greater than 100%."
        )

    start_year = (
        int(param2)
        if pd.notna(param2) and param2 != 0
        else YEAR_MIN
    )

    end_year = (
        int(param3)
        if pd.notna(param3) and param3 != 0
        else YEAR_MAX
    )

    if start_year > end_year:
        raise ValueError(
            "Production adjustment start year cannot be after "
            "the end year."
        )

    production_metrics = [
        "Equity Accounted Gas Production",
        "Equity Accounted NGL Production",
        "Equity Accounted Oil Production",
        "Equity Accounted Total Production (mboed)",
        "Gas - Non-Revenue Generating Prod (mmscfd)",
        "Gas Production (mmscf/d)",
        "Liquids Production (mboed)",
        "NGL - Non-Revenue Generating Prod (mbd)",
        "NGL Production (mb/d)",
        "Oil - Non-Revenue Generating Prod (mbd)",
        "Oil Production (mb/d)",
        "Revenue Generating Total Prod (mboe)",
        "Revenue Generating Total Prod (mboed)",
        "Total Production (mboed)"
    ]

    driver_metrics = [
        "Gross Margin",
        "Production Costs",
        "Total Cash Costs",
        "DD&A Charge"
    ]

    year_mask = (
        (result["Year"] >= start_year)
        & (result["Year"] <= end_year)
    )

    # Capture the financial-driver deltas before changing the values.
    driver_rows = result.loc[
        result["Metric"].isin(driver_metrics) & year_mask,
        ["Metric", "Year", "Value"]
    ].copy()

    duplicate_rows = driver_rows.duplicated(
        subset=["Metric", "Year"],
        keep=False
    )

    if duplicate_rows.any():
        duplicates = (
            driver_rows.loc[
                duplicate_rows,
                ["Metric", "Year"]
            ]
            .drop_duplicates()
            .sort_values(["Metric", "Year"])
            .to_dict("records")
        )

        raise ValueError(
            "Expected one row per financial driver and year. "
            f"Duplicates found: {duplicates}."
        )

    driver_rows["Delta"] = (
        driver_rows["Value"].fillna(0)
        * production_change
    )

    delta_table = (
        driver_rows
        .pivot(
            index="Year",
            columns="Metric",
            values="Delta"
        )
        .reindex(columns=driver_metrics)
        .fillna(0)
    )

    # Scale all available production metrics.
    production_mask = (
        result["Metric"].isin(production_metrics)
        & year_mask
    )

    result.loc[production_mask, "Value"] = (
        result.loc[production_mask, "Value"]
        * (1 + production_change)
    )

    # Scale the direct financial drivers.
    driver_mask = (
        result["Metric"].isin(driver_metrics)
        & year_mask
    )

    result.loc[driver_mask, "Value"] = (
        result.loc[driver_mask, "Value"]
        * (1 + production_change)
    )

    calculated_metric_map = {
        "EBITDA": [
            "Gross Margin",
            "Total Cash Costs"
        ],
        "Underlying RCOP": [
            "Gross Margin",
            "Total Cash Costs",
            "DD&A Charge"
        ],
        "Operating Cashflow": [
            "Gross Margin",
            "Total Cash Costs"
        ],
        "Pre Tax Cash Flow": [
            "Gross Margin",
            "Total Cash Costs"
        ]
    }

    for metric, delta_components in calculated_metric_map.items():

        metric_mask = (
            (result["Metric"] == metric)
            & year_mask
        )

        if not metric_mask.any():
            raise ValueError(
                f"Metric '{metric}' does not exist in the case profile."
            )

        metric_years = result.loc[
            metric_mask,
            "Year"
        ]

        row_delta = pd.Series(
            0.0,
            index=metric_years.index
        )

        for component in delta_components:
            row_delta = (
                row_delta
                + metric_years.map(
                    delta_table[component]
                ).fillna(0)
            )

        result.loc[metric_mask, "Value"] = (
            result.loc[metric_mask, "Value"].fillna(0)
            + row_delta
        )

    return result

##############################
## OPERATION == Δ OPEX % #####
##############################

## This function is the main code block for the proportional OPEX adjustment operation.
## It works by scaling Total Cash Costs by the OPEX change and propagating the resulting financial delta to EBITDA, Underlying RCOP, Operating Cashflow and Pre Tax Cash Flow.
## It assumes that the OPEX change is expressed as a decimal fraction, e.g. 0.10 = 10% increase, -0.10 = 10% reduction, -1.00 = 100% reduction.

def apply_CostAdjOpex(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Apply a percentage adjustment to Total Cash Costs and propagate
    the resulting financial delta to related earnings and cash metrics.

    Parameters
    ----------
    param1 : float
        Percentage adjustment expressed as a decimal fraction.

        Examples:
         0.10 = 10% increase in costs
        -0.10 = 10% reduction in costs

    param2 : int, optional
        First year in which the adjustment applies.
        Defaults to YEAR_MIN.

    param3 : int, optional
        Final year in which the adjustment applies.
        Defaults to YEAR_MAX.

    param4, param5
        Reserved for future use.
    """

    result = df.copy()

    if pd.isna(param1):
        return result

    opex_change = float(param1)

    if opex_change < -1:
        raise ValueError(
            "OPEX reduction cannot be greater than 100%."
        )

    start_year = (
        int(param2)
        if pd.notna(param2) and param2 != 0
        else YEAR_MIN
    )

    end_year = (
        int(param3)
        if pd.notna(param3) and param3 != 0
        else YEAR_MAX
    )

    if start_year > end_year:
        raise ValueError(
            "OPEX adjustment start year cannot be after the end year."
        )

    base_metric = "Total Cash Costs"

    impacted_metrics = [
        "Total Cash Costs",
        "EBITDA",
        "Underlying RCOP",
        "Operating Cashflow",
        "Pre Tax Cash Flow"
    ]

    base_rows = result.loc[
        result["Metric"] == base_metric,
        ["Year", "Value"]
    ].copy()

    if base_rows.empty:
        raise ValueError(
            f"Metric '{base_metric}' does not exist in the case profile."
        )

    duplicate_years = base_rows["Year"].duplicated(
        keep=False
    )

    if duplicate_years.any():
        duplicated = sorted(
            base_rows.loc[duplicate_years, "Year"]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Expected one '{base_metric}' row per year, but found "
            f"duplicates for years: {duplicated}."
        )

    base_cost_by_year = base_rows.set_index(
        "Year"
    )["Value"]

    opex_delta_by_year = (
        base_cost_by_year
        * opex_change
    )

    adjustment_mask = (
        result["Metric"].isin(impacted_metrics)
        & (result["Year"] >= start_year)
        & (result["Year"] <= end_year)
    )

    row_deltas = (
        result.loc[adjustment_mask, "Year"]
        .map(opex_delta_by_year)
        .fillna(0)
    )

    result.loc[adjustment_mask, "Value"] = (
        result.loc[adjustment_mask, "Value"].fillna(0)
        + row_deltas
    )

    return result

##############################
## OPERATION == Δ CAPEX % ####
##############################

## This function is the main code block for the proportional CAPEX adjustment operation.
## It works by scaling Cash Capex by the CAPEX change and propagating the resulting financial delta to Pre Tax Cash Flow.
## It assumes that the CAPEX change is expressed as a decimal fraction, e.g. 0.10 = 10% increase, -0.10 = 10% reduction, -1.00 = 100% reduction.

def apply_CostAdjCapex(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Apply a percentage adjustment to Cash Capex and propagate
    the resulting delta to Pre Tax Cash Flow.

    Parameters
    ----------
    param1 : float
        Percentage adjustment expressed as a decimal fraction.

        Examples:
         0.10 = 10% increase in CAPEX
        -0.10 = 10% reduction in CAPEX

    param2 : int, optional
        First year in which the adjustment applies.
        Defaults to YEAR_MIN.

    param3 : int, optional
        Final year in which the adjustment applies.
        Defaults to YEAR_MAX.

    param4, param5
        Reserved for future use.
    """

    result = df.copy()

    if pd.isna(param1):
        return result

    capex_change = float(param1)

    if capex_change < -1:
        raise ValueError(
            "CAPEX reduction cannot be greater than 100%."
        )

    start_year = (
        int(param2)
        if pd.notna(param2) and param2 != 0
        else YEAR_MIN
    )

    end_year = (
        int(param3)
        if pd.notna(param3) and param3 != 0
        else YEAR_MAX
    )

    if start_year > end_year:
        raise ValueError(
            "CAPEX adjustment start year cannot be after the end year."
        )

    base_metric = "Cash Capex"

    impacted_metrics = [
        "Cash Capex",
        "Pre Tax Cash Flow"
    ]

    base_rows = result.loc[
        result["Metric"] == base_metric,
        ["Year", "Value"]
    ].copy()

    if base_rows.empty:
        raise ValueError(
            f"Metric '{base_metric}' does not exist in the case profile."
        )

    duplicate_years = base_rows["Year"].duplicated(
        keep=False
    )

    if duplicate_years.any():
        duplicated = sorted(
            base_rows.loc[
                duplicate_years,
                "Year"
            ].unique().tolist()
        )

        raise ValueError(
            f"Expected one '{base_metric}' row per year, but found "
            f"duplicates for years: {duplicated}."
        )

    base_capex_by_year = (
        base_rows
        .set_index("Year")["Value"]
    )

    capex_delta_by_year = (
        base_capex_by_year
        * capex_change
    )

    adjustment_mask = (
        result["Metric"].isin(impacted_metrics)
        & (result["Year"] >= start_year)
        & (result["Year"] <= end_year)
    )

    row_deltas = (
        result.loc[
            adjustment_mask,
            "Year"
        ]
        .map(capex_delta_by_year)
        .fillna(0)
    )

    result.loc[adjustment_mask, "Value"] = (
        result.loc[
            adjustment_mask,
            "Value"
        ].fillna(0)
        + row_deltas
    )

    return result


##############################
## OPERATION == Δ CAPEX $ ####
##############################

## This function is the main code block for the absolute CAPEX adjustment operation.
## It works by directly adjusting Cash Capex and propagating the resulting financial delta to Pre Tax Cash Flow.
## It assumes that the CAPEX adjustments are expressed in $m.

def apply_CapexAbsolute(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Apply up to two absolute Cash Capex adjustments.

    Parameters
    ----------
    param1 : float, optional
        First CAPEX adjustment in $m.

        Positive value = additional CAPEX.
        Negative value = CAPEX reduction.

    param2 : int, optional
        Calendar year for the first adjustment.

    param3 : float, optional
        Second CAPEX adjustment in $m.

        Positive value = additional CAPEX.
        Negative value = CAPEX reduction.

    param4 : int, optional
        Calendar year for the second adjustment.

    param5
        Reserved for future use.

    Notes
    -----
    Cash Capex and Pre Tax Cash Flow use the model's cash-flow sign
    convention. Therefore, a positive user input creates a negative
    adjustment to both metrics.
    """

    result = df.copy()

    impacted_metrics = [
        "Cash Capex",
        "Pre Tax Cash Flow"
    ]

    adjustments = [
        (param1, param2),
        (param3, param4)
    ]

    for adjustment_amount, adjustment_year in adjustments:

        # Scenario preparation converts blank numeric parameters to zero.
        # Therefore zero is treated as "not supplied" for pair validation.
        amount_missing = (
            pd.isna(adjustment_amount)
            or float(adjustment_amount) == 0
        )

        year_missing = (
            pd.isna(adjustment_year)
            or int(adjustment_year) == 0
        )

        # Both blank / zero means this adjustment pair is unused.
        if amount_missing and year_missing:
            continue

        # One supplied without the other is an invalid configuration.
        if amount_missing or year_missing:
            raise ValueError(
                "Each CAPEX adjustment requires both an "
                "adjustment amount and an adjustment year."
            )

        adjustment_amount = float(
            adjustment_amount
        )

        adjustment_year = int(
            adjustment_year
        )

        if adjustment_year < YEAR_MIN or adjustment_year > YEAR_MAX:
            raise ValueError(
                f"CAPEX adjustment year {adjustment_year} falls "
                f"outside the model horizon "
                f"{YEAR_MIN}–{YEAR_MAX}."
            )

        # Positive input means additional CAPEX, which is negative
        # under the model's cash-flow sign convention.
        capex_delta = -adjustment_amount

        for metric in impacted_metrics:

            metric_year_mask = (
                (result["Metric"] == metric)
                & (result["Year"] == adjustment_year)
            )

            matching_rows = int(
                metric_year_mask.sum()
            )

            if matching_rows > 1:
                raise ValueError(
                    f"Expected no more than one '{metric}' row for "
                    f"{adjustment_year}, but found {matching_rows}."
                )

            if matching_rows == 0:
                raise ValueError(
                    f"Metric '{metric}' is missing for "
                    f"{adjustment_year}."
                )

            result.loc[
                metric_year_mask,
                "Value"
            ] = (
                result.loc[
                    metric_year_mask,
                    "Value"
                ].fillna(0)
                + capex_delta
            )

    return result

##############################
## OPERATION == Δ OPEX $ #####
##############################

## This function is the main code block for the absolute OPEX adjustment operation.
## It works by directly adjusting OPEX and propagating the resulting financial delta to Pre Tax Cash Flow.
## It assumes that the OPEX adjustments are expressed in $m.

def apply_CashCostAbsolute(
    df,
    param1=None,
    param2=None,
    param3=None,
    param4=None,
    param5=None
):
    """
    Apply up to two absolute Total Cash Costs adjustments.

    Parameters
    ----------
    param1 : float, optional
        First cash-cost adjustment in $m.

        Positive value = additional cash cost.
        Negative value = cash-cost reduction.

    param2 : int, optional
        Calendar year for the first adjustment.

    param3 : float, optional
        Second cash-cost adjustment in $m.

        Positive value = additional cash cost.
        Negative value = cash-cost reduction.

    param4 : int, optional
        Calendar year for the second adjustment.

    param5
        Reserved for future use.

    Notes
    -----
    Total Cash Costs are stored as negative values.

    Therefore:
        Positive input  = additional cost = negative profile delta
        Negative input  = cost reduction  = positive profile delta

    The same monetary delta is applied to:
        - Total Cash Costs
        - Underlying RCOP
        - Operating Cashflow
        - Pre Tax Cash Flow
    """

    result = df.copy()

    impacted_metrics = [
        "Total Cash Costs",
        "Underlying RCOP",
        "Operating Cashflow",
        "Pre Tax Cash Flow"
    ]

    adjustments = [
        (param1, param2),
        (param3, param4)
    ]

    for adjustment_amount, adjustment_year in adjustments:

        # Scenario preparation converts blank numeric parameters to zero.
        # Therefore zero is treated as "not supplied" for pair validation.
        amount_missing = (
            pd.isna(adjustment_amount)
            or float(adjustment_amount) == 0
        )

        year_missing = (
            pd.isna(adjustment_year)
            or int(adjustment_year) == 0
        )

        # Both blank / zero means this adjustment pair is unused.
        if amount_missing and year_missing:
            continue

        # One supplied without the other is an invalid configuration.
        if amount_missing or year_missing:
            raise ValueError(
                "Each cash-cost adjustment requires both an "
                "adjustment amount and an adjustment year."
            )

        adjustment_amount = float(
            adjustment_amount
        )

        adjustment_year = int(
            adjustment_year
        )

        if adjustment_year < YEAR_MIN or adjustment_year > YEAR_MAX:
            raise ValueError(
                f"Cash-cost adjustment year {adjustment_year} falls "
                f"outside the model horizon "
                f"{YEAR_MIN}–{YEAR_MAX}."
            )

        # Positive user input means additional cost.
        # Costs are negative in the model.
        cash_cost_delta = -adjustment_amount

        for metric in impacted_metrics:

            metric_year_mask = (
                (result["Metric"] == metric)
                & (result["Year"] == adjustment_year)
            )

            matching_rows = int(
                metric_year_mask.sum()
            )

            if matching_rows > 1:
                raise ValueError(
                    f"Expected no more than one '{metric}' row for "
                    f"{adjustment_year}, but found {matching_rows}."
                )

            if matching_rows == 0:
                raise ValueError(
                    f"Metric '{metric}' is missing for "
                    f"{adjustment_year}."
                )

            result.loc[
                metric_year_mask,
                "Value"
            ] = (
                result.loc[
                    metric_year_mask,
                    "Value"
                ].fillna(0)
                + cash_cost_delta
            )

    return result


# ============================================================
# FUNCTION MAP
# ============================================================

## This dictionary maps the operation names in the Excel instructions
## to the corresponding Python functions defined above.
## The keys must match the operation names in the Excel instructions exactly.
## The values must be the names of the functions defined above, without parentheses.
## The functions are called dynamically using the dictionary mapping, so they must be defined before the dictionary is created.

operation_functions = {
    "Delay": apply_delay,
    "Accelerate": apply_accelerate,
    "Increase": apply_increase,
    "Dilution": apply_dilution,
    "CostAdjOpex":apply_CostAdjOpex,
    "CostAdjCapex":apply_CostAdjCapex,
    "CapexAbsolute":apply_CapexAbsolute,
    "OpexAbsolute":apply_CashCostAbsolute,
    "ProdnAdj": apply_ProdnAdj,
    "TruncateBefore": apply_truncate_before,
    "TruncateAfter": apply_truncate_after,
    "NoChange": apply_nochange   
}
