"""This file contains the bracketing function to find the next critical point"""

import numpy as np

def bracketing(model, tol=1e-7, max_steps=100, raise_error=True, **options):
    """Finds next critical point

    The bracketing function finds the next critical point starting from a models
    state.
    - A first nonlinear step needs to be solved already.
    - Det(K) has to be solved for the model.

    1. The algorithm searches for a sign change of Det(K).
        This is done by using a 'last-increment-prediction' and 'arc-length-control'
    2. A bisection algorithm is used to find the Det(K)=0 point.
        Again 'arc-length-control' strategy is used.

    Parameters
    ----------
    model : Model
        initial model for the bracketing function. A first step needs to be already solved
    tol : float
        tolerance for Det(K)==0
    max_steps : int
        maximum number of steps for the iterative search
    options :
        additional options for the nonlinear solution
    """

    print("=================================")
    print("Starting bracketing to search for next critical point.")


    if 'solve_attendant_eigenvalue' in options:
        solve_attendant_eigenvalue = options['solve_attendant_eigenvalue']
    else:
        solve_attendant_eigenvalue = True

    # naming convention indices:
    # _0: current
    # _1: previous
    # _2: second previous

    model_0 = model
    model_1 = model.get_previous_model()
    model_2 = None
    initial_model = model_0

    if model_0.det_k is None:
        model_0.solve_det_k()
    det_k_0 = model_0.det_k
    
    if model_1.det_k is None:
        model_1.solve_det_k()
    det_k_1 = model_1.det_k

    det_k_2 = None

    delta_0 = det_k_0 - det_k_1
    delta_1 = delta_0

    in_min_max = False
    bisectioning = False

    success = False
    step = 0
    while step < max_steps and not success:

        # check if critical point has been found
        if abs(det_k_0) < tol:
            print('Converged to Det(K) = {}'.format(det_k_0))
            success = True
            break
        elif abs(det_k_0 / initial_model.det_k) < tol:
            print('Converged to relative value Det(K)/Det(K)_initial = {}'.format(det_k_0 / initial_model.det_k))
            success = True
            break
        elif abs(det_k_0 - det_k_1) < tol:
            print('WARNING: Converged at stationary point for Det(K)!')
            success = True
            break

        step += 1
        print('=================================')
        print('Bracketing step {}'.format(step))

        if not in_min_max and np.sign(det_k_0) == np.sign(det_k_1) and np.sign(delta_0) == np.sign(delta_1):
            
            print('  Arclength step...')

            model_0 = model_0.get_duplicate()

            model_0.predict_tangential(strategy="arc-length")

            model_0.perform_non_linear_solution_step(strategy='arc-length-control',
                                                solve_det_k=True,
                                                solve_attendant_eigenvalue=solve_attendant_eigenvalue,
                                                **options)

        elif bisectioning or np.sign(det_k_0) != np.sign(det_k_1):
            # sign of the determinant changed, target is between det_k_1 and det_k_0
            bisectioning = True
            print('  Bisectioning to find critical point.')
            model_0 = bisection(model_0)

        elif in_min_max or np.sign(delta_0) != np.sign(delta_1):
            # sign of delta changed target is between det_k_2 and det_k_0
            in_min_max = True
            print('  Search for local miimum/maximum.')
            model_0 = minmax(model_0)
        else:
            raise RuntimeError('Unhandled case in bracketing function!')

        # update the local variables
        model_1 = model_0.get_previous_model()
        model_2 = model_1.get_previous_model()

        det_k_2 = model_2.det_k
        det_k_1 = model_1.det_k
        det_k_0 = model_0.det_k

        delta_1 = det_k_1 - det_k_2
        delta_0 = det_k_0 - det_k_1


    if not success:
        msg = 'Bracketing: No critical point found!'
        if raise_error:
            raise RuntimeError(msg)
        else:
            prinit(msg)
    return model_0


def minmax(model):
    """does a 3-point node search for a local mininmum/maximum. where model is the middle point.
    It returns the estimated position inside model +- arclength"""

    model_1 = model.get_previous_model()
    model_2 = model
    model_3 = model_2.get_duplicate()
    
    model_3.predict_tangential(strategy="arc-length")

    model_3.perform_non_linear_solution_step(strategy='arc-length-control',
                                        solve_det_k=True,
                                        solve_attendant_eigenvalue=True)

    x1 = 0.0 
    x2 = np.linalg.norm(model_2.get_increment_vector())
    x3 = x2 + np.linalg.norm(model_3.get_increment_vector())
    y1 = model_1.det_k
    y2 = model_2.det_k 
    y3 = model_3.det_k

    denom = (x1 - x2) * (x1 - x3) * (x2 - x3) 
    A = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom 
    B = (x3*x3 * (y1 - y2) + x2*x2 * (y3 - y1) + x1*x1 * (y2 - y3)) / denom 
    C = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom 
    xv = -B / (2*A) 
    #yv = C - B*B / (4*A) 

    if xv >= x3:
        return model_3
    elif xv >= x2:
        model = model_2.get_duplicate()
        
        model.predict_tangential(strategy="arc-length")

        model.scale_prediction((xv-x2)/(x3-x2))
        
        model.perform_non_linear_solution_step(strategy='arc-length-control',
                                            solve_det_k=True,
                                            solve_attendant_eigenvalue=True)
        return model

    elif xv >= x1:
        model = model_1.get_duplicate()
        
        model.predict_tangential(strategy="arc-length")

        model.scale_prediction((xv)/(x2))
        
        model.perform_non_linear_solution_step(strategy='arc-length-control',
                                            solve_det_k=True,
                                            solve_attendant_eigenvalue=True)

        return model
    else:
        print("  WARNING: Miniimum/maximum has been already passed!")
        return model


def bisection(model):
    """does a bisectioning to find the root of det_k, between model and its previous model.
    returns the new upper bound"""
    lower_limit_model = model.get_previous_model()
    upper_limit_model = model

    tmp_model = lower_limit_model.get_duplicate()

    for node in tmp_model.nodes:
        lower_node = lower_limit_model.get_node(id=node.id)
        upper_node = upper_limit_model.get_node(id=node.id)

        node.u = (lower_node.u + upper_node.u)/2
        node.v = (lower_node.v + upper_node.v)/2
        node.w = (lower_node.w + upper_node.w)/2

    tmp_model.lam = (lower_limit_model.lam + upper_limit_model.lam)/2

    tmp_model.perform_non_linear_solution_step(strategy='arc-length-control',
                                        solve_det_k=True,
                                        solve_attendant_eigenvalue=True)

    if np.sign(lower_limit_model.det_k) == np.sign(tmp_model.det_k):
        model._previous_model = tmp_model
    else:
        model = tmp_model

    return model
