def optimize_fun_drink_params():
    from simulation import TradingEngine
    from algorithm_v3 import Algorithm
    from scipy.optimize import differential_evolution

    def objective(params):
        # Unpack and cast parameters for the SMA strategy.
        sma_window = int(round(params[0]))
        trade_size = int(round(params[1]))

        # Enforce basic constraints.
        if sma_window < 2 or trade_size < 100:
            return 1e6  # Large penalty if below realistic values.

        pnl_sum = 0.0
        n_runs = 3  # Average over multiple simulation runs.
        for _ in range(n_runs):
            engine = TradingEngine()
            # Override only the Fun Drink parameters, merging with the default config.
            config = {
                "Fun Drink": {
                    "sma_window": sma_window,
                    "trade_size": trade_size,
                }
            }
            algo = Algorithm(positions=engine.positions, config=config)
            engine.run_algorithms(algo, output_daily_to_CLI=False)
            pnl_sum += float(engine.get_total_PnL())
        avg_pnl = pnl_sum / n_runs
        # Since we want to maximize PnL, we return its negative.
        return -avg_pnl

    # Use a mutable counter to track iterations
    iteration = [0]

    def callback(xk, convergence):
        iteration[0] += 1
        sma_window = int(round(xk[0]))
        trade_size = int(round(xk[1]))
        current_pnl = -objective(xk)
        print(
            f"Iteration {iteration[0]}: Current best: SMA_window = {sma_window}, Trade_size = {trade_size}, PnL = {current_pnl:.2f}")

    # Set bounds that cover a broad range, including values that might match the default config.
    bounds = [
        (2, 40),  # sma_window: allow from 2 up to 40 days.
        (100, 10000)  # trade_size: from 100 units up to 10,000 (should cover your default if it was high)
    ]

    result = differential_evolution(
        objective, bounds,
        popsize=15,
        maxiter=200,
        disp=True,
        polish=True,
        callback=callback
    )

    optimal_sma_window = int(round(result.x[0]))
    optimal_trade_size = int(round(result.x[1]))
    max_pnl = -result.fun

    print("Optimal SMA_window:", optimal_sma_window)
    print("Optimal Trade_size:", optimal_trade_size)
    print("Maximum Total PnL:", max_pnl)


if __name__ == '__main__':
    optimize_fun_drink_params()
