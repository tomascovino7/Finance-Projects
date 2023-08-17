import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def get_float_input(prompt):
    return float(input(prompt))

def get_date_input(prompt):
    date_string = input(prompt)
    return ql.Date(*map(int, date_string.split('-')))

def create_european_option(K, option_type, T):
    payoff = ql.PlainVanillaPayoff(option_type, K)
    exercise = ql.EuropeanExercise(T)
    return ql.VanillaOption(payoff, exercise)

def main():
    while True:
        try:
            S = get_float_input("Enter the current stock price (S):")
            K = get_float_input("Enter the current strike price (K):")
            div = get_float_input("Enter the dividend yield (div):")
            r = get_float_input("Enter the risk-free interest rate (r):")
            Today = get_date_input("Enter the current date (DD-MM-YYYY):")
            T = get_date_input("Enter the option expiration date (DD-MM-YYYY):")
            Sigma = get_float_input("Enter the volatility (Sigma):")
            
            option_type_input = input("Select option type (Put or Call): ").strip().lower()
            if option_type_input not in ["put", "call"]:
                raise ValueError("Invalid option type selected. Defaulting to Put.")
            
            option_position_input = input("Select your position (Long or Short):").strip().lower()
            if option_position_input not in ["long", "short"]:
                raise ValueError("Invalid position type")
            
            put_call_parity_input = input("Do you want the Put-Call Parity proof? (Yes or No):").strip().lower()
            if put_call_parity_input not in ["yes", "no"]:
                raise ValueError("Invalid, its not that dificult just write yes or no")          
              
            option_type = ql.Option.Put if option_type_input == "put" else ql.Option.Call
            
            european_option = create_european_option(K, option_type, T)
            Day_Convention = ql.Actual365Fixed()
            Calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
            
            spot_handle = ql.QuoteHandle(ql.SimpleQuote(S))
            flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(Today, r, Day_Convention))
            dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(Today, div, Day_Convention))
            flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(Today, Calendar, Sigma, Day_Convention))
            
            BSM_Process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)
            

            Days = T - Today
            t = Days/365
            
            #Black Scholes Pricing model
            european_option.setPricingEngine(ql.AnalyticEuropeanEngine(BSM_Process))
            bs_price = european_option.NPV()
            
            print("-------------------------------------------------------------------------")
            print("Black Scholes Price = %lf" % bs_price)
            print("Day count =", Days)
            
            call = ql.Option.Call
            put = ql.Option.Put

            def EuropeanCall(K, call, T):
                Payoff = ql.PlainVanillaPayoff(call, K)
                exercise = ql.EuropeanExercise(T)
                return ql.VanillaOption(Payoff, exercise)

            def EuropeanPut(K, put, T):
                Payoff = ql.PlainVanillaPayoff(put, K)
                exercise = ql.EuropeanExercise(T)
                return ql.VanillaOption(Payoff, exercise)

            Call = EuropeanCall(K, call, T)
            Put = EuropeanPut(K, put, T)

            Call.setPricingEngine(ql.AnalyticEuropeanEngine(BSM_Process))
            Cprice = Call.NPV()
            Put.setPricingEngine(ql.AnalyticEuropeanEngine(BSM_Process))
            Pprice = Put.NPV()
            
            # Calculate option payoffs for different stock prices
            stock_prices = np.linspace(0.8 * S, 1.2 * S, 100) #Revisar
            Longcall_payoffs = [max(S - K, 0) for S in stock_prices]
            Longput_payoffs = [max(K - S, 0) for S in stock_prices]   
            Shortcall_payoffs = [-max(S - K, 0) for S in stock_prices]
            Shortput_payoffs = [-max(K - S, 0) for S in stock_prices]
            
            if option_type_input == "call" and option_position_input == "long":
                breakeven_price = K + Cprice
                option_payoffs = Longcall_payoffs
                option_label = 'Long Call Payoff'
                
            elif option_type_input =="call" and option_position_input =="short":
                breakeven_price = K + Cprice
                option_payoffs = Shortcall_payoffs
                option_label = 'Short Call Payoff'
                
            elif option_type_input =="put" and option_position_input =="long":
                breakeven_price = K - Pprice
                option_payoffs = Longput_payoffs
                option_label = 'Long Put Payoff'
                
            else:
                breakeven_price = K - Pprice
                option_payoffs = Shortput_payoffs
                option_label = 'Short Put Payoff' 

            Call_Parity = Cprice + K * np.exp(-r*t)
            Put_Parity = Pprice + S * np.exp(-div*t)
            
            print("Breakeven at: ", round(breakeven_price,2))
                                
            if put_call_parity_input == "yes":
                if round(Call_Parity, 4) == round(Put_Parity, 4):
                    print("-------------------------------------------------------------------------")
                    print("Call Price (C):", round(Cprice,2))
                    print("Put Price (P):", round(Pprice, 2))
                    print("Put-Call parity proof:")
                    print("C + K * e^(-r*t) = P + S * e^(-div*t)")
                    print(round(Cprice, 2), "+", K, "*", "e^","(",-r,"*",round(t,2),")","=",round(Pprice, 2),"+",S,"* e^(",-div,"*",round(t,2),")")
                    print(round(Call_Parity,2), "=", round(Put_Parity,2))
                else:
                    print("There's no Put-Call parity, remember that for it to happen both instruments must have the same strike, maturity and underlying asset")    
            else: 
                break 
            
            
            
            # Plot the selected option's payoff
            plt.plot(stock_prices, option_payoffs, label=option_label)
            plt.axvline(K, color='red', linestyle='--', linewidth=0.8, label='Strike Price')
            plt.axvline(breakeven_price, color='green', linestyle='--', linewidth=0.8, label='Breakeven Point')
            plt.axhline(bs_price, color='black', linestyle='-', linewidth=0.8)
            plt.xlabel('Stock Price')
            plt.ylabel('Payoff')
            plt.title('Option Payoff')
            plt.legend()
            plt.grid(True)
            plt.show()
            break 
            
        except (ValueError, Exception) as e:
            print("An error occurred:", e)
            print("Please check your inputs and try again.\n")

if __name__ == "__main__":
    main()
