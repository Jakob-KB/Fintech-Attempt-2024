def optimize_fintech_token_sma_window():
    from simulation import TradingEngine
    from algorithm import Algorithm
    from scipy.optimize import differential_evolution

    def objective(params):
        # Optimize only the fintech token SMA window.
        (sma_window,) = params

        # Convert to an integer value (SMA window should be a whole number)
        sma_window = int(round(sma_window))

        # Fixed UQ Dollar bounds
        lower_bound = 99.9
        upper_bound = 100.0

        pnl_sum = 0
        n_runs = 3  # Average over multiple runs to reduce noise
        for _ in range(n_runs):
            engine = TradingEngine()
            # Build config with fixed UQ Dollar bounds and optimized Fintech Token SMA window
            config = {
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "fintech_token_sma_window": sma_window
            }
            algo = Algorithm(positions=engine.positions, config=config)
            engine.run_algorithms(algo, output_daily_to_CLI=False)
            pnl_sum += float(engine.get_total_PnL())
        avg_pnl = pnl_sum / n_runs

        # We want to maximize PnL, so we return negative average PnL.
        return -avg_pnl

    def callback(xk, convergence):
        sma_window = int(round(xk[0]))
        current_pnl = -objective(xk)
        print(f"Current best SMA window: {sma_window}, PnL: {current_pnl:.2f}")

    # Define search bounds for the fintech token SMA window.
    # For example, test SMA windows between 10 and 50 days.
    bounds = [(10, 50)]
    result = differential_evolution(
        objective,
        bounds,
        popsize=20,
        maxiter=1000,
        disp=True,
        polish=True,
        callback=callback
    )

    optimal_sma_window = int(round(result.x[0]))
    max_pnl = -result.fun
    print("Optimal Fintech Token SMA window:", optimal_sma_window)
    print("Maximum Total PnL:", max_pnl)


if __name__ == '__main__':
    optimize_fintech_token_sma_window()
