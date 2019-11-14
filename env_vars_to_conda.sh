source unset_env_vars.sh
source env_variables.sh
mkdir -p $CONDA_PREFIX/etc/conda/activate.d/
mkdir -p $CONDA_PREFIX/etc/conda/deactivate.d/
cp env_variables.sh $CONDA_PREFIX/etc/conda/activate.d/
cp unset_env_vars.sh $CONDA_PREFIX/etc/conda/deactivate.d/