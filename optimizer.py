def optimize_instrument_params(
        instrument,
        param_names,
        bounds,
        conversion_funcs,
        algo_class,
        simulation_engine_class,
        n_runs=3,
        constraint_func=None
):
    from scipy.optimize import differential_evolution

    # Mutable counter for tracking iterations
    iteration = [0]

    def objective(params):
        # Convert optimizer parameters to their proper types
        param_values = {}
        for i, name in enumerate(param_names):
            conv = conversion_funcs[i] if conversion_funcs and i < len(conversion_funcs) else (lambda x: x)
            param_values[name] = conv(params[i])

        # Apply any constraint function (should return 0 if no violation, >0 otherwise)
        if constraint_func:
            penalty = constraint_func(param_values)
            if penalty > 0:
                return 1e6 + penalty  # Large penalty for violating constraints

        # Run the simulation several times to reduce noise
        pnl_sum = 0.0
        for _ in range(n_runs):
            engine = simulation_engine_class()
            # Merge the optimized parameters into the instrument's config.
            config = {instrument: param_values}
            algo = algo_class(positions=engine.positions, config=config)
            engine.run_algorithms(algo, output_daily_to_CLI=False)
            pnl_sum += float(engine.get_total_PnL())
        avg_pnl = pnl_sum / n_runs
        # We want to maximize profit, so return the negative of average PnL.
        return -avg_pnl

    def callback(xk, convergence):
        iteration[0] += 1
        current_params = {}
        for i, name in enumerate(param_names):
            conv = conversion_funcs[i] if conversion_funcs and i < len(conversion_funcs) else (lambda x: x)
            current_params[name] = conv(xk[i])
        current_pnl = -objective(xk)
        param_str = ', '.join(f"{name}={value}" for name, value in current_params.items())
        print(f"Iteration {iteration[0]}: Current best: {param_str}, PnL = {current_pnl:.2f}")

    # Run the differential evolution optimizer
    result = differential_evolution(
        objective, bounds,
        popsize=5,
        maxiter=200,
        disp=True,
        polish=True,
        callback=callback
    )

    # Extract and print the optimal parameters.
    optimal_params = {}
    for i, name in enumerate(param_names):
        conv = conversion_funcs[i] if conversion_funcs and i < len(conversion_funcs) else (lambda x: x)
        optimal_params[name] = conv(result.x[i])
    max_pnl = -result.fun

    print(f"\nOptimal parameters for {instrument}:")
    for name, value in optimal_params.items():
        print(f"  {name}: {value}")
    print("Maximum Total PnL:", max_pnl)

    return optimal_params, max_pnl


# Example usage:
if __name__ == '__main__':
    # Import your classes.
    from algorithm_v3 import Algorithm
    from simulation import TradingEngine

    # For example, to optimize the "Fun Drink" instrument for parameters "sma_window" and "trade_size":
    param_names = ["ema_window", "trade_size"]
    bounds = [
        (2, 40),  # Bound for sma_window (e.g. 2 to 40 days)
        (100, 10000)  # Bound for trade_size (e.g. 100 to 10,000 units)
    ]
    conversion_funcs = [lambda x: int(round(x)), lambda x: int(round(x))]

    optimize_instrument_params(
        instrument="Fun Drink",
        param_names=param_names,
        bounds=bounds,
        conversion_funcs=conversion_funcs,
        algo_class=Algorithm,
        simulation_engine_class=TradingEngine,
        n_runs=3,
        constraint_func=None
    )
