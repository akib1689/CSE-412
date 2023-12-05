'''
This is a single server queueing system simulation.
Theory can be found from the book of "Simulation Modeling and Analysis" by Averill M. Law and W. David Kelton.
'''


# constants to be used as a server state
IDLE = 0
BUSY = 1

# queue limit
Q_LIMIT = 100

# input file name
INPUT_FILE_NAME = 'in.txt'

# output file name
OUTPUT_FILE_NAME = 'results.txt'

EVENT_LOG = 'event_orders.txt'

output_file = None
event_log = None

# import the random number generator
from lcg_rand import Lcgrand

# import math
import math

# global variables
next_event_type = num_custs_delayed = num_delays_required = num_events = num_in_q = 0
server_status = IDLE
area_num_in_q = area_server_status = mean_interarrival = mean_service = sim_time = time_last_event = total_of_delays = 0.0
time_arrival = [0.0] * (Q_LIMIT + 1)
time_next_event = [0.0] * 3
num_custs_arrived = 0
num_custs_departed = 0
event_count = 0
lcg = Lcgrand()

# expon function
def expon(mean):
    global lcg
    return -mean * math.log(lcg.lcgrand(1))
        
# init function of the simulation
def initialize():
    global sim_time, server_status, num_in_q, time_last_event
    global num_custs_delayed, total_of_delays, area_num_in_q, area_server_status
    global time_next_event, mean_interarrival
    global num_custs_arrived, num_custs_departed

    # Initialize the simulation clock.
    sim_time = 0.0

    # Initialize the state variables.
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0

    # Initialize the statistical counters.
    num_custs_delayed = 0
    num_custs_arrived = 0
    num_custs_departed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0

    # Initialize event list. Since no customers are present, the departure
    # (service completion) event is eliminated from consideration.
    time_next_event = [0, sim_time + expon(mean_interarrival), 1.0e+30]
    
# timing function for the simulation
def timing():
    global sim_time, time_next_event, num_events, next_event_type, event_count
    
    min_time_next_event = 1.0e+29
    next_event_type = 0
    
    # Determine the event type of the next event to occur.
    for i in range(1, num_events + 1):
        if (time_next_event[i] < min_time_next_event):
            min_time_next_event = time_next_event[i]
            next_event_type = i
    
    
    # Check to see whether the event list is empty.
    if next_event_type == 0:
        # The event list is empty, so stop the simulation.
        print('Event list empty at time ' + str(sim_time))
        exit(1)
    
    # The event list is not empty, so advance the simulation clock.
    sim_time = min_time_next_event
    event_count += 1
    
    
# arrival event function for the simulation
def arrive():
    global sim_time, time_next_event, mean_interarrival, server_status, num_in_q, Q_LIMIT, time_arrival, total_of_delays, num_custs_delayed, mean_service
    
    global event_log, event_count
    global num_custs_arrived

    # Schedule next arrival.
    time_next_event[1] = sim_time + expon(mean_interarrival)
    
    # increment the number of customers arrived
    num_custs_arrived += 1
    
    # log the event
    event_log.write(str(event_count) + '. Next event: Customer ' + str(num_custs_arrived) + ' Arrival\n' )
    

    # Check to see whether server is busy.
    if (server_status == BUSY):
        # Server is busy, so increment number of customers in queue.
        num_in_q += 1

        # Check to see whether an overflow condition exists.
        if num_in_q > Q_LIMIT:
            # The queue has overflowed, so stop the simulation.
            print("\nOverflow of the array time_arrival at time", sim_time)
            exit(2)

        # There is still room in the queue, so store the time of arrival of the arriving customer at the (new) end of time_arrival.
        time_arrival[num_in_q] = sim_time
    else:
        # Server is idle, so arriving customer has a delay of zero.
        delay = 0.0
        total_of_delays += delay

        # Increment the number of customers delayed, and make server busy.
        num_custs_delayed += 1
        
        # log the event
        event_log.write('\n---------No. of customers delayed: ' + str(num_custs_delayed) + '--------\n\n')
        server_status = BUSY

        # Schedule a departure (service completion).
        time_next_event[2] = sim_time + expon(mean_service)
        
    
# departure event function for the simulation
def depart():
    global sim_time, num_in_q, server_status, time_next_event, time_arrival, total_of_delays, num_custs_delayed, mean_service
    
    global event_log, event_count
    global num_custs_departed
    
    # increment the number of customers departed
    num_custs_departed += 1
    
    # log the event
    event_log.write(str(event_count) + '. Next event: Customer ' + str(num_custs_departed) + ' Departure\n' )

    # Check to see whether the queue is empty.
    if num_in_q == 0:
        # The queue is empty so make the server idle and eliminate the departure (service completion) event from consideration.
        server_status = IDLE
        time_next_event[2] = 1.0e+30
    else:
        # The queue is nonempty, so decrement the number of customers in queue.
        num_in_q -= 1

        # Compute the delay of the customer who is beginning service and update the total delay accumulator.
        delay = sim_time - time_arrival[1]
        total_of_delays += delay

        # Increment the number of customers delayed, and schedule departure.
        num_custs_delayed += 1
        
        # log the event
        event_log.write('\n---------No. of customers delayed: ' + str(num_custs_delayed) + '--------\n\n')
        
        time_next_event[2] = sim_time + expon(mean_service)

        # Move each customer in queue (if any) up one place.
        for i in range(1, num_in_q + 1):
            time_arrival[i] = time_arrival[i + 1]



# report function for the simulation
def report():
    global total_of_delays, num_custs_delayed, area_num_in_q, sim_time, area_server_status
    
    global output_file

    # Compute and write estimates of desired measures of performance. to the output file
    output_file.write("\nAvg delay in queue: {:.6f} minutes\n".format(total_of_delays / num_custs_delayed))
    output_file.write("Avg number in queue: {:.6f}\n".format(area_num_in_q / sim_time))
    output_file.write("Server utilization: {:.6f}\n".format(area_server_status / sim_time))
    output_file.write("Time simulation ended: {:.6f} minutes".format(sim_time))
    
# update_time_avg_stats function for the simulation
def update_time_avg_stats():
    global sim_time, time_last_event, area_num_in_q, area_server_status, num_in_q, server_status

    # Compute time since last event, and update last-event-time marker.
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    # Update area under number-in-queue function.
    area_num_in_q += num_in_q * time_since_last_event

    # Update area under server-busy indicator function.
    area_server_status += server_status * time_since_last_event
    
    
# function to print all the global variables
def print_globals():
    print('sim_time: ' + str(sim_time))
    print('server_status: ' + str(server_status))
    print('num_in_q: ' + str(num_in_q))
    print('time_last_event: ' + str(time_last_event))
    print('num_custs_delayed: ' + str(num_custs_delayed))
    print('total_of_delays: ' + str(total_of_delays))
    print('area_num_in_q: ' + str(area_num_in_q))
    print('area_server_status: ' + str(area_server_status))
    print('time_next_event: ' + str(time_next_event))
    print('mean_interarrival: ' + str(mean_interarrival))
    print('mean_service: ' + str(mean_service))
    print('num_delays_required: ' + str(num_delays_required))
    print('next_event_type: ' + str(next_event_type))
    exit(1)
    
# main function of the simulation
def main():
    global num_events, mean_interarrival, mean_service, num_delays_required, num_custs_delayed, next_event_type
    
    global output_file, event_log

    # Specify the number of events for the timing function.
    num_events = 2

    # Read input parameters. from the input file
    with open(INPUT_FILE_NAME, 'r') as input_file:
        # Read input parameters. 1 line seperated by space
        
        mean_interarrival, mean_service, num_delays_required = map(float, input_file.readline().split())
        # convert to the num_delays_required to integer
        num_delays_required = int(num_delays_required)
        
    # create the output file and event log file
    output_file = open(OUTPUT_FILE_NAME, 'w')
    event_log = open(EVENT_LOG, 'w')
        

    # Write report heading and input parameters. to the output file
    output_file.write("----Single-Server Queueing System----\n\n")
    output_file.write("Mean inter-arrival time: {:.6f} minutes\n".format(mean_interarrival))
    output_file.write("Mean service time: {:.6f} minutes\n".format(mean_service))
    output_file.write("Number of customers: {:d}\n".format(num_delays_required))
    # Initialize the simulation.
    initialize()
        

    # Run the simulation while more delays are still needed.
    while num_custs_delayed < num_delays_required:
        # Determine the next event.
        timing()
        
        # Update time-average statistical accumulators.
        update_time_avg_stats()

        # Invoke the appropriate event function.
        if next_event_type == 1:
            arrive()
        elif next_event_type == 2:
            depart()

    # Invoke the report generator and end the simulation.
    report()

if __name__ == "__main__":
    main()