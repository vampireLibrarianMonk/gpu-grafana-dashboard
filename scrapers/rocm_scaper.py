import json
from utilities import utilities_rocm_gpu

utilities_rocm_gpu.get_gpu_info()

def get_rocm_smi_output():
    metrics = utilities_rocm_gpu.get_gpu_info()

    return metrics

def main():
    try:
        metrics = get_rocm_smi_output()
        print(json.dumps(metrics, indent=4))
    except RuntimeError as err:
        print(err)


if __name__ == '__main__':
    main()
