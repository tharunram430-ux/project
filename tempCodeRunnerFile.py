, KFold, RepeatedStratifiedKFold, LeaveOneOut,
    learning_curve, validation_curve
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import RFE
from sklearn.inspection import permutation_importance

from sklearn.linear_model im