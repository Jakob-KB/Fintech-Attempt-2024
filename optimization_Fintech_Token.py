def optimize_fintech_params():
    from simulation import TradingEngine
    from algorithm import Algorithm
    from scipy.optimize import differential_evolution

    def objective(params):
        # Unpack and cast parameters: ensure integer values for SMA days.
        short_term = int(round(params[0]))
        long_term = int(round(params[1]))
        diff_threshold = float(params[2])

        # Enforce constraint: short_term must be less than long_term.
        if short_term >= long_term:
            return 1e6 + (short_term - long_term) ** 2

        pnl_sum = 0.0
        n_runs = 3  # average over multiple runs to reduce noise
        for _ in range(n_runs):
            engine = TradingEngine()
            # Pass the parameters to your algorithm config.
            config = {
                "short_term_SMA_days": short_term,
                "long_term_SMA_days": long_term,
                "difference_threshold": diff_threshold,
            }
            algo = Algorithm(positions=engine.positions, config=config)
            engine.run_algorithms(algo, output_daily_to_CLI=False)
            pnl_sum += float(engine.get_total_PnL())
        avg_pnl = pnl_sum / n_runs

        # Since we want to maximize PnL, return its negative.
        return -avg_pnl

    def callback(xk, convergence):
        short_term = int(round(xk[0]))
        long_term = int(round(xk[1]))
        diff_threshold = xk[2]
        current_pnl = -objective(xk)
        print(f"Current best: short_term_SMA_days = {short_term}, "
              f"long_term_SMA_days = {long_term}, "
              f"difference_threshold = {diff_threshold:.2f}, PnL = {current_pnl:.2f}")

    # Define the parameter bounds.
    # Here, short_term_SMA_days is between 3 and 14,
    # long_term_SMA_days is between 15 and 60,
    # and difference_threshold is between 1 and 50.
    bounds = [(3, 14), (15, 60), (1, 50)]
    result = differential_evolution(
        objective, bounds,
        popsize=20,
        maxiter=1000,
        disp=True,
        polish=True,
        callback=callback
    )

    optimal_short = int(round(result.x[0]))
    optimal_long = int(round(result.x[1]))
    optimal_diff = result.x[2]
    max_pnl = -result.fun

    print("Optimal short term SMA days:", optimal_short)
    print("Optimal long term SMA days:", optimal_long)
    print("Optimal difference threshold:", optimal_diff)
    print("Maximum Total PnL:", max_pnl)

if __name__ == '__main__':
    optimize_fintech_params()
