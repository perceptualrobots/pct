# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/16_environment_processing.ipynb.

# %% auto 0
__all__ = ['wind_turbine_results', 'EnvironmentProcessingFactory', 'BaseEnvironmentProcessing',
           'WindTurbineEnvironmentProcessing', 'DummyEnvironmentProcessing', 'ARCEnvironmentProcessing']

# %% ../nbs/16_environment_processing.ipynb 3
from abc import ABC, abstractmethod
from comet_ml import Experiment, api
from comet_ml import Artifact
from os import sep, makedirs, path
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import time


# %% ../nbs/16_environment_processing.ipynb 4
from .yaw_module import get_comparaison_metrics, test_trad_control, test_hpct_wind, get_properties, get_indexes
from .putils import printtime, NumberStats, PCTRunProperties
from .helpers import SolutionsDataManager, ChallengesDataManager
from .hierarchy import PCTHierarchy

# %% ../nbs/16_environment_processing.ipynb 7
def wind_turbine_results(environment_properties=None, experiment=None, root=None, wt='WindTurbine', verbose=None, early=None, min=None,
                         comparisons=False, comparisons_print_plots=False, property_dir=None, property_file=None, plots=None, log_testing_to_experiment=False):

    prefix = property_file[:property_file.find(".properties")]
    filename=wt+sep+property_dir+sep+property_file
    file = root + 'data'+sep+'ga'+sep+ filename

    wind_timeseries,start, stop, model_params,yaw_params,keep_history, rt = get_properties(environment_properties)

    history=True
    series = environment_properties['series']
    outdir='c:'+sep+'tmp'+sep+'WindTurbine'+ sep + environment_properties['range'] + sep + series + sep + prefix +sep
    makedirs(outdir, exist_ok=True)

    # lastsepIndex = filename.rfind(sep)
    # propIndex = filename.rfind('.properties')
    # filenamePrefix = filename[lastsepIndex+1:propIndex]
    # draw_file = outdir + 'draw-'+filenamePrefix+'.png'
    draw_file = False
    model_file = outdir + 'res_model.html'

    if experiment:
        artifact = Artifact(property_file, "Properties file")
        artifact.add(file)
        experiment.log_artifact(artifact)

    (res_model, nac_pos_model, power_improvement, power_control, power_simu) = test_hpct_wind(
        file=file,plots=plots,history=history,verbose=verbose,outdir=outdir,early=early,draw_file=draw_file, model_file=model_file,
        environment_properties=environment_properties,
        start_index=model_params['start_index_test'],
        stop_index=model_params['stop_index_test'],
        experiment=experiment,
        datatype='test',
        log_testing_to_experiment=log_testing_to_experiment, min=min
        )

    if comparisons:
        start, stop = get_indexes(model_params, environment_properties)

        (res_baseline_simu, nac_pos_baseline_simu, wind_dir) = test_trad_control(
            model_params['wind_timeseries'],
            model_params['wind_timeseries_not_agg'],
            yaw_params['cycle_period'],
            start, #model_params['start_index_test'],
            stop, #model_params['stop_index_test'],
            experiment=experiment,
            datatype='baseline_simu',
            outdir=outdir
            )

        (res_baseline_logs, nac_pos_baseline_logs, wind_dir) = test_trad_control(
            model_params['wind_timeseries'],
            model_params['wind_timeseries_not_agg'],
            yaw_params['cycle_period'],
            start, #model_params['start_index_test'],
            stop, #model_params['stop_index_test'],
            experiment=experiment,
            datatype='baseline_logs',
            outdir=outdir
            )

    rel_net_prod_change=[]
    net_prod_change=[]
    if comparisons :
        power_prod_change, conso_yaw_change, net_prod_change, rel_net_prod_change,yaw_error_rel_change = get_comparaison_metrics(wind_dir,power_control,power_simu,nac_pos_model, nac_pos_baseline_simu, yaw_params['yaw_rate_max'], yaw_params['yaw_consumption'], 50)    

        if comparisons_print_plots:
            fig, axs = plt.subplots(6, sharex=True, figsize=(15,25), gridspec_kw={'height_ratios': [3, 1, 1,1,1,1]})
            plt.xlabel('time (sec)', fontsize=20)
            plt.xlim(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'])

            axs[0].plot(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']),wind_dir,label='wind direction')
            axs[0].plot(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']),nac_pos_model,linewidth=4.0, label='nacelle position RL algorithm')
            axs[0].plot(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'],yaw_params['cycle_period'] ),nac_pos_baseline_simu,linewidth=4.0, label='nacelle position simulated baseline algorithm')
            axs[0].plot(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']),nac_pos_baseline_logs,linewidth=4.0, label='nacelle position baseline algorithm from logs')
            axs[0].legend(fontsize=20)
            axs[0].tick_params(labelsize=20)
            axs[0].set_ylabel(ylabel='angle (deg)', fontsize=20)

            axs[1].bar(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']*50),yaw_error_rel_change,500,linewidth=4.0, label='RL alg', align='edge')
            axs[1].get_yaxis().set_major_formatter(FuncFormatter(lambda y, _: "{:.1f}%".format(y)))
            axs[1].legend(fontsize=20)
            axs[1].tick_params(labelsize=20)
            axs[1].set_ylabel(ylabel='yaw misaligment \ndecrease (per cent)', fontsize=20,)

            axs[2].bar(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']*50),power_prod_change,500,linewidth=4.0, label='RL alg', align='edge')
            plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: "{:.1f}%".format(y)))
            axs[2].legend(fontsize=20)
            axs[2].tick_params(labelsize=20)
            axs[2].set_ylabel(ylabel='power output \nincrease (kW)', fontsize=20,)

            axs[3].bar(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']*50),conso_yaw_change,500,linewidth=4.0, label='RL alg', align='edge')
            plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: "{:.1f}%".format(y)))
            axs[3].legend(fontsize=20)
            axs[3].tick_params(labelsize=20)
            axs[3].set_ylabel(ylabel='yaw consumption \nincrease (kW)', fontsize=20,)

            axs[4].bar(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']*50),net_prod_change,500,linewidth=4.0, label='RL alg', align='edge')
            axs[4].legend(fontsize=20)
            axs[4].tick_params(labelsize=20)
            axs[4].set_ylabel(ylabel='net power output \nincrease (kW)', fontsize=20,)

            axs[5].bar(range(0,(model_params['stop_index_test']- model_params['start_index_test'])*yaw_params['cycle_period'] ,yaw_params['cycle_period']*50),rel_net_prod_change,500,linewidth=4.0, label='RL alg', align='edge')
            axs[5].get_yaxis().set_major_formatter(FuncFormatter(lambda y, _: "{:.1f}%".format(y)))
            axs[5].legend(fontsize=20)
            axs[5].tick_params(labelsize=20)
            axs[5].set_ylabel(ylabel='net power output \nincrease (per cent)', fontsize=20,)

            fig.tight_layout()
            plt.savefig(outdir + f'{series}_dataset',dpi=600)


            fig, axs = plt.subplots(2, sharex=True)
            axs[0].plot(range(model_params['start_index']*yaw_params['cycle_period'],model_params['stop_index']*yaw_params['cycle_period'], yaw_params['cycle_period'] ),wind_timeseries['wind_direction'][model_params['start_index']:model_params['stop_index']],label='train')
            axs[0].plot(range(model_params['start_index_test']*yaw_params['cycle_period'],model_params['stop_index_test']*yaw_params['cycle_period'],yaw_params['cycle_period'] ),wind_timeseries['wind_direction'][model_params['start_index_test']: model_params['stop_index_test']],label='test')
            plt.xlabel('time (sec)')
            axs[1].plot(range(model_params['start_index']*yaw_params['cycle_period'],model_params['stop_index']*yaw_params['cycle_period'], yaw_params['cycle_period'] ),wind_timeseries['wind_speed'][model_params['start_index']:model_params['stop_index']],label='train')
            axs[1].plot(range(model_params['start_index_test']*yaw_params['cycle_period'],model_params['stop_index_test']*yaw_params['cycle_period'],yaw_params['cycle_period'] ),wind_timeseries['wind_speed'][model_params['start_index_test']: model_params['stop_index_test']],label='test')
            plt.setp(axs[1], ylabel='wind speed (m/s)')
            plt.setp(axs[0], ylabel='wind direction (deg)')
            plt.legend()
            plt.savefig(outdir + f'{series}_results',dpi=1000)

    average_yaw_error_decrease_base = 0
    average_yaw_error_decrease_simu = 0

    if comparisons:    
        print(res_baseline_logs)
        print(res_baseline_simu)
        average_yaw_error_decrease_base = 100 * (res_baseline_logs['average yaw error_baseline_logs'] - res_model['average yaw error'])/res_baseline_logs['average yaw error_baseline_logs']
        average_yaw_error_decrease_simu = 100 * (res_baseline_simu['average yaw error_baseline_simu'] - res_model['average yaw error'])/res_baseline_simu['average yaw error_baseline_simu']

    print(res_model)

    print(f'average_yaw_error_decrease_base={average_yaw_error_decrease_base:4.2f}')
    print(f'average_yaw_error_decrease_simu={average_yaw_error_decrease_simu:4.2f}')

    energy_gain =  100*(res_model['power_control']/res_model['power_trad']-1)
    net_energy_gain = ( ( (sum(net_prod_change) + res_model['power_trad'])/res_model['power_trad'])-1) * 100

    if experiment:
        experiment.log_metric('pc_test_result', res_model['power_control'])
        experiment.log_metric('yaw_count', res_model['yaw count'])
        experiment.log_metric('mean_ye', res_model['average yaw error'])
        experiment.log_metric('energy_gain', energy_gain)
        experiment.log_metric('net_eg', net_energy_gain)
        experiment.log_metric('avg_ye_dec_base', average_yaw_error_decrease_base)
        experiment.log_metric('avg_ye_dec_simu', average_yaw_error_decrease_simu)


    return energy_gain, net_energy_gain, power_improvement, power_prod_change, conso_yaw_change, net_prod_change,rel_net_prod_change,yaw_error_rel_change



# %% ../nbs/16_environment_processing.ipynb 10
class EnvironmentProcessingFactory:
    factories = {}
    def addFactory(id, environmentProcessingFactory):
        EnvironmentProcessingFactory.factories.put[id] = environmentProcessingFactory
    addFactory = staticmethod(addFactory)
    
    # A Template Method:
    def createEnvironmentProcessing(id):
        if not EnvironmentProcessingFactory.factories.__contains__(id):
            EnvironmentProcessingFactory.factories[id] = \
              eval(id + '.Factory()')
        return EnvironmentProcessingFactory.factories[id].create()
    
    createEnvironmentProcessing = staticmethod(createEnvironmentProcessing)       


# %% ../nbs/16_environment_processing.ipynb 12
class BaseEnvironmentProcessing(ABC):
    "Base class of environment processing."
    # def __init__(self):

    def set_properties(self, args):
        self.args = args
        self.env_processing_details={}

    def get_file_props(self, filepath):
        if filepath.find(sep) < 0:
            file = filepath
            property_dir = ""
        else:
            index1=filepath.rindex(sep)
            file = filepath[index1+1:]
            index2=filepath.rindex(sep, 0, index1)
            property_dir=filepath[index2+1:index1]
        drive=self.args['drive']

        return drive, property_dir, file

    def add_processing_detail(self, key, value):
        self.env_processing_details[key]=value

    def add_details(self, details):
        if details is not None:
            for key, value in details.items():
                self.env_processing_details[key]=value

    def enhanced_environment_properties(self, environment_properties=None):
        pass


    def get_experiment(self):
        if self.args and 'project_name' in self.args and self.args['project_name']:
            # env_name=self.args['env_name']
            # filename=self.args['file']
            # root = self.args['root_path']
            # pfile = root + self.args['configs_dir'] + env_name +sep+ filename + ".properties"

            final_ex_name = self.get_experiment_name()
            if not self.args['overwrite']:
                capi = api.API(api_key=self.args['api_key'])
                while True:
                    connected = False
                    try:
                        experiment_exists = capi.get( workspace=self.args['workspace'] + '/' + self.args['project_name'] +'/' + final_ex_name)
                        connected = True
                    except Exception as e:
                        print ('type is:', e.__class__.__name__)
                        # print(experiment_exists)
                        print('Sleeping for 5 ...')
                        time.sleep(5)

                    if connected:
                        break

                if experiment_exists:
                    print("Experiment", final_ex_name, "already exists in", self.args['project_name'])
                    return None, True


            experiment = Experiment(api_key=self.args['api_key'],
                                    project_name=self.args['project_name'],
                                    workspace=self.args['workspace'], display_summary_level=0)

            # experiment.log_parameters(model_params)
            # experiment.log_code(path.basename(__file__))	
            experiment.set_name(final_ex_name)
        else:
            experiment = None

        self.start = printtime('Start')
        return experiment, None

    def get_experiment_name(self):
        filename=self.args['file']

        prefix = filename[2:6]	
        final_ex_name = f'{prefix}-{self.args["seed"]:02}'

        return final_ex_name
    
    @abstractmethod
    def results(self, filepath=None, experiment=None):
        return None

    @abstractmethod
    def get_workspace(self):
        return 'wind-turbine'
    



# %% ../nbs/16_environment_processing.ipynb 14
class WindTurbineEnvironmentProcessing(BaseEnvironmentProcessing):
    "WindTurbine environment processing."
    # def __init__(self):

    def get_experiment_name(self):
        env_name=self.args['env_name']
        filename=self.args['file']
        root = self.args['root_path']
        pfile = root + self.args['configs_dir'] + env_name +sep+ filename + ".properties"

        ep, en = PCTRunProperties.get_environment_properties_from_filename(pfile)
        ex_name = ep['series']
        self.args['experiment_name']= ex_name
        self.args['project_name'] = self.args['project_name']+"-" + ex_name

        prefix = filename[2:6]	
        final_ex_name = f'{ex_name[0:1]}-{prefix}-{self.args["seed"]:02}'

        return final_ex_name

    def get_workspace(self):
        return 'wind-turbine'
    
    def results(self, filepath=None, experiment=None):
        environment_properties=None
        plots=None
        early=None

        if 'log_testing_to_experiment' in self.args:
            log_testing_to_experiment =  self.args['log_testing_to_experiment']
        else:
            log_testing_to_experiment = False


        drive, property_dir, file = self.get_file_props(filepath=filepath)

        if environment_properties is None:
            environment_properties, en = PCTRunProperties.get_environment_properties(root=drive, env='WindTurbine', property_dir=property_dir, property_file=file)
            environment_properties['keep_history'] = True
            environment_properties['range'] = 'test'
            print(environment_properties)

        energy_gain, net_energy_gain, _ , _, _, _,_,_ = wind_turbine_results(environment_properties=environment_properties, experiment=experiment, root=drive, 
                            verbose=self.args['verbosed']['hpct_verbose'], early=early, comparisons=self.args['comparisons'], 
                            comparisons_print_plots=self.args['comparisons_print_plots'], min= not self.args['max'],
                            property_dir=property_dir, property_file=file, plots=plots, log_testing_to_experiment=log_testing_to_experiment)

        print(f'energy_gain = {energy_gain:4.2f}')
        print(f'net_energy_gain = {net_energy_gain:4.2f}')

        end = printtime('End')	
        elapsed = end-self.start        
        print(f'Elapsed time: {elapsed:4.2f}')
        NumberStats.getInstance().report()
        if experiment:
            experiment.end()

        return {'energy_gain' : energy_gain, 'net_energy_gain' : net_energy_gain}


    class Factory:
        def create(self): return WindTurbineEnvironmentProcessing()

# %% ../nbs/16_environment_processing.ipynb 15
class DummyEnvironmentProcessing(BaseEnvironmentProcessing):
    "Dummy environment processing."

    def get_workspace(self):
        return 'dummy'
    
    def results(self, filepath=None, experiment=None):

        return {}


    class Factory:
        def create(self): return DummyEnvironmentProcessing()

# %% ../nbs/16_environment_processing.ipynb 17
class ARCEnvironmentProcessing(BaseEnvironmentProcessing):
    "ARC environment processing."

    def get_workspace(self):
        return 'arc-challenge'
    
    def enhanced_environment_properties(self, environment_properties=None):
        enhanced_environment_properties = {}
        if 'dir' in environment_properties:
            dir = environment_properties['dir']
        else:
            dir = 'C:\\packages\\arc-prize-2024'
            environment_properties['dir'] = dir 

        if 'file_prefix' in environment_properties:
            file_prefix = environment_properties['file_prefix']
        else:
            file_prefix = 'arc-agi_training_'
            environment_properties['file_prefix'] = file_prefix

        file_name = path.join(dir, file_prefix) + 'challenges.json' 
        challenges_manager = ChallengesDataManager(file_name)
        data = challenges_manager.get_data_for_key(environment_properties['code'])
        enhanced_environment_properties['data']=data

        solutions_file = path.join(environment_properties['dir'], environment_properties['file_prefix']) + 'solutions.json' 
        solutions_manager = SolutionsDataManager(solutions_file)
        test_output_array = solutions_manager.get_data_for_key(environment_properties['code'])
        enhanced_environment_properties['test_output_array']=test_output_array

        return enhanced_environment_properties
    
    def results(self, filepath=None, experiment=None):
        print(filepath)
        environment_properties=None
        drive, property_dir, file = self.get_file_props(filepath=filepath)
        if environment_properties is None:
            environment_properties, en = PCTRunProperties.get_environment_properties(root=drive, env='ARC', property_dir=property_dir, property_file=file)
            environment_properties['dataset'] = 'test'
            print(environment_properties)

        enhanced_environment_properties = self.enhanced_environment_properties(environment_properties=environment_properties)

        verbose= self.args['verbosed']['hpct_verbose'] 
        min= not self.args['max']
        history=True

        hierarchy, score = PCTHierarchy.run_from_file(filepath, env_props=environment_properties, history=history, hpct_verbose= verbose, render=self.args['verbosed']['display_env'],
                                                  runs=None, experiment=experiment, min=min, enhanced_environment_properties=enhanced_environment_properties)

        # hierarchy, score = PCTHierarchy.run_from_file(filepath, env_props=environment_properties, plots=plots, history=history, hpct_verbose= verbose, 
        #                                           runs=None, plots_dir=outdir, early_termination=early, draw_file=draw_file, experiment=experiment, 
        #                                           log_experiment_figure=log_experiment_figure, min=min)

        # hierarchy, env = PCTHierarchy.load_from_file(filepath, min=min, render=False, history=history, env_props=environment_properties, hpct_verbose= verbose)
        # score, dfig, pfigs = PCTHierarchy.run_and_draw_hierarchy(hierarchy, env, draw_file=True, draw_figsize=(5,5), history = history, plots="scEdges,scZero", steps=5)#, draw_file='/tmp/tmp.png')


        print('Test score',score)
        fitness_list = str( [f'{i:4.3f}' for i in  self.env_processing_details['fitness_list']])
        print('fitness_list', fitness_list)

        if experiment:         
            grid = hierarchy.get_grid()
            experiment.log_other('LxC', f'{len(grid)}x{max(grid)}')
            indstr = 'all'
            if 'index' in environment_properties:
                indstr = str(environment_properties['index'])
            experiment.log_other('index', indstr)
            experiment.log_other('fitness_list', fitness_list)
            input_set = environment_properties['input_set']
            experiment.log_other('input_set', str(input_set))
            experiment.log_metric('last_gen', self.env_processing_details['last_gen'])
            experiment.log_metric('fitness', self.env_processing_details['fitness'])
            experiment.log_other('test_score', f'{score:4.3f}')

        return {}


    def get_experiment_name(self):
        filename=self.args['file']

        prefix = filename[3:7]	
        final_ex_name = f'{prefix}-{self.args["seed"]:02}'

        return final_ex_name


    class Factory:
        def create(self): return ARCEnvironmentProcessing()
