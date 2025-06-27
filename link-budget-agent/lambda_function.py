import json
import logging
import sys
import os

# Add the link-budget package to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the link-budget modules
from linkbudget import calc, constants, propagation, pointing, util, antenna, cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda function handler for link budget calculations
    
    Parameters:
    -----------
    event : dict
        Input event containing parameters for link budget calculation
        If parameters are not provided, sensible defaults will be used
    
    context : object
        Lambda context object
    
    Returns:
    --------
    dict
        Link budget calculation results in Amazon Bedrock action group format
    """
    try:
        # Check if this is a Bedrock Agent request
        is_bedrock_agent = 'messageVersion' in event and 'actionGroup' in event
        
        # Extract parameters based on the request type
        if is_bedrock_agent:
            # Extract parameters from Bedrock Agent request
            params = {}
            parameters_list = event.get('parameters', [])
            for param in parameters_list:
                name = param.get('name')
                value = param.get('value')
                # Convert string values to appropriate types
                if name in ['freq', 'bw']:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                elif name in ['eirp', 'obo', 'rx_dish_size', 'rx_dish_gain', 'rx_dish_efficiency', 
                             'lnb_noise_fig', 'lnb_gain', 'rx_noise_fig', 'coax_length',
                             'rx_long', 'rx_lat', 'sat_long', 'slant_range', 'min_cnr', 'impl_margin']:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                params[name] = value
                
            # Specifically log rx_dish_gain and coax_length for debugging
            logger.info(f"Extracted rx_dish_gain: {params.get('rx_dish_gain')}")
            logger.info(f"Extracted coax_length: {params.get('coax_length')}")
            
            # Get action group and function name
            action_group = event.get('actionGroup', 'LinkBudgetCalculator')
            function_name = event.get('function', 'calculateLinkBudget')
        else:
            # Standard Lambda invocation
            params = event.get('parameters', {})
            action_group = 'LinkBudgetCalculator'
            function_name = 'calculateLinkBudget'
        
        # Required parameters with sensible defaults
        freq = params.get('freq', 12e9)  # 12 GHz (Ku-band)
        bw = params.get('bw', 36e6)      # 36 MHz transponder
        
        # Tx parameters
        eirp = params.get('eirp', 50)    # 50 dBW EIRP (typical for satellite transponder)
        obo = params.get('obo', 0)       # Output backoff in dB
        
        # Rx parameters
        # Note: Only one of rx_dish_size or rx_dish_gain should be used
        # If both are provided, rx_dish_gain takes precedence
        rx_dish_size = params.get('rx_dish_size', 0.9)  # 90cm dish
        rx_dish_gain = params.get('rx_dish_gain', 33)   # 33 dBi gain (alternative to dish size)
        rx_dish_efficiency = params.get('rx_dish_efficiency', 0.65)  # 65% efficiency
        lnb_noise_fig = params.get('lnb_noise_fig', 0.7)  # 0.7 dB noise figure
        lnb_gain = params.get('lnb_gain', 55)  # 55 dB gain
        rx_noise_fig = params.get('rx_noise_fig', 8)  # 8 dB noise figure
        coax_length = params.get('coax_length', 50)  # 50 ft coax
        
        # Position parameters (optional)
        rx_long = params.get('rx_long', None)
        rx_lat = params.get('rx_lat', None)
        sat_long = params.get('sat_long', None)
        slant_range = params.get('slant_range', 38000)  # ~38000 km for GEO satellite
        
        # Polarization
        polarization = params.get('polarization', 'linear')
        
        # Margin parameters
        min_cnr = params.get('min_cnr', 8)  # 8 dB minimum CNR
        impl_margin = params.get('impl_margin', 1)  # 1 dB implementation margin
        
        # Create a class to mimic argparse namespace
        class Args:
            pass
        
        args = Args()
        
        # Set all required parameters
        args.freq = freq
        args.bw = bw
        args.eirp = eirp
        args.obo = obo
        args.rx_dish_efficiency = rx_dish_efficiency
        args.lnb_noise_fig = lnb_noise_fig
        args.lnb_gain = lnb_gain
        args.rx_noise_fig = rx_noise_fig
        args.coax_length = coax_length
        logger.info(f"Using coax_length: {coax_length} ft")
        args.polarization = polarization
        args.min_cnr = min_cnr
        args.impl_margin = impl_margin
        args.slant_range = slant_range
        
        # Set either rx_dish_size or rx_dish_gain (rx_dish_gain takes precedence)
        if 'rx_dish_gain' in params:
            args.rx_dish_gain = rx_dish_gain
            args.rx_dish_size = None
            logger.info(f"Using rx_dish_gain: {rx_dish_gain} dBi (taking precedence over rx_dish_size)")
        else:
            args.rx_dish_size = rx_dish_size
            args.rx_dish_gain = None
            logger.info(f"Using rx_dish_size: {rx_dish_size} m")
        
        # Add optional position parameters if provided
        if rx_long is not None and rx_lat is not None and sat_long is not None:
            args.rx_long = rx_long
            args.rx_lat = rx_lat
            args.sat_long = sat_long
            args.slant_range = None  # Override slant_range if coordinates are provided
        else:
            args.rx_long = None
            args.rx_lat = None
            args.sat_long = None
        
        # Set defaults for other parameters
        args.rx_height = 0
        args.sat_lat = 0
        args.sat_alt = constants.GEOSYNC_ORBIT
        args.ref_ellipsoid = 'WGS84'
        args.atmospheric_loss = 0.5  # Set a default atmospheric loss of 0.5 dB
        args.availability = 99
        args.asi = False
        args.mispointing_loss = 0
        args.lna_feed_loss = 0
        args.antenna_noise_temp = None
        args.sat_tle_name = None
        args.obs_time = None
        args.radar = False
        args.json = True
        args.tx_dish_size = None
        args.tx_dish_gain = None
        args.tx_dish_efficiency = 0.56
        args.tx_power = None
        args.carrier_peb = None
        args.tp_bw = None
        args.lnb_noise_temp = None
        args.sat_tle_group = None
        args.tle_save_dir = pointing.get_default_tle_dataset_dir()
        args.tle_no_save = False
        args.radar_cross_section = None
        
        # Run the link budget analysis
        results = cli.analyze(args, verbose=False)
        
        # Format the response based on the request type
        if is_bedrock_agent:
            # Return in Bedrock Agent action group format
            response_body = {
                'TEXT': {
                    'body': json.dumps({
                        'message': 'Link budget calculation successful',
                        'results': results
                    })
                }
            }
            
            function_response = {
                'actionGroup': action_group,
                'function': function_name,
                'functionResponse': {
                    'responseBody': response_body
                }
            }
            
            # Get session attributes if they exist
            session_attributes = event.get('sessionAttributes', {})
            prompt_session_attributes = event.get('promptSessionAttributes', {})
            
            return {
                'messageVersion': '1.0',
                'response': function_response,
                'sessionAttributes': session_attributes,
                'promptSessionAttributes': prompt_session_attributes
            }
        else:
            # Return in standard Lambda format for backward compatibility
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Link budget calculation successful',
                    'results': results
                })
            }
    
    except Exception as e:
        logger.error(f"Error calculating link budget: {str(e)}")
        
        if 'messageVersion' in event:
            # Return error in Bedrock Agent format
            action_group = event.get('actionGroup', 'LinkBudgetCalculator')
            function_name = event.get('function', 'calculateLinkBudget')
            
            response_body = {
                'TEXT': {
                    'body': json.dumps({
                        'message': f'Error calculating link budget: {str(e)}',
                        'error': True
                    })
                }
            }
            
            function_response = {
                'actionGroup': action_group,
                'function': function_name,
                'functionResponse': {
                    'responseState': 'FAILURE',
                    'responseBody': response_body
                }
            }
            
            return {
                'messageVersion': '1.0',
                'response': function_response,
                'sessionAttributes': event.get('sessionAttributes', {}),
                'promptSessionAttributes': event.get('promptSessionAttributes', {})
            }
        else:
            # Return error in standard Lambda format
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': f'Error calculating link budget: {str(e)}'
                })
            }

# For local testing
if __name__ == "__main__":
    # Test with default parameters
    test_event = {'parameters': {}}
    print(json.dumps(lambda_handler(test_event, None), indent=2))
    
    # Test with Bedrock Agent format
    test_bedrock_event = {
        'messageVersion': '1.0',
        'actionGroup': 'LinkBudgetCalculator',
        'function': 'calculateLinkBudget',
        'parameters': [
            {'name': 'freq', 'type': 'number', 'value': '14000000000'},
            {'name': 'eirp', 'type': 'number', 'value': '55'},
            {'name': 'rx_dish_size', 'type': 'number', 'value': '1.2'},
            {'name': 'rx_dish_gain', 'type': 'number', 'value': '35'},
            {'name': 'coax_length', 'type': 'number', 'value': '75'}
        ],
        'sessionAttributes': {},
        'promptSessionAttributes': {}
    }
    print("\nTesting Bedrock Agent format:")
    print(json.dumps(lambda_handler(test_bedrock_event, None), indent=2))
