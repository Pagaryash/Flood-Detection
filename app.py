# app.py – UI UPGRADED VERSION (Streamlit)
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from sklearn.metrics import confusion_matrix

# ========================================
# 1. SET PROJECT ROOT
# ========================================
try:
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    os.chdir(PROJECT_ROOT)
except NameError:
    PROJECT_ROOT = os.getcwd()
    os.chdir(PROJECT_ROOT)

# ========================================
# 2. PAGE CONFIG
# ========================================
st.set_page_config(
    page_title="Flood AI: U-Net vs DeepLabV3+",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# 2.1 GLOBAL UI CSS (NO EXTRA LIBS)
# ========================================
st.markdown(
    """
<style>
/* Layout */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }
h1, h2, h3 { letter-spacing: 0.2px; }

/* Metric cards */
[data-testid="stMetric"] {
  background: rgba(255,255,255,0.04);
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
  font-size: 16px;
  padding: 10px 14px;
}

/* Images */
img { border-radius: 14px; }
</style>
""",
    unsafe_allow_html=True
)

# ========================================
# 3. LOAD DATA
# ========================================
@st.cache_data
def load_data():
    data_path = os.path.join(PROJECT_ROOT, "data", "processed")

    metrics = np.load(os.path.join(data_path, "metrics.npy"), allow_pickle=True).item()
    pred_unet = np.load(os.path.join(data_path, "pred_unet.npy"))
    pred_deeplab = np.load(os.path.join(data_path, "pred_deeplab.npy"))
    X_val = np.load(os.path.join(data_path, "X_val.npy"))
    y_val = np.load(os.path.join(data_path, "y_val.npy"))
    indices = np.arange(len(X_val))

    return metrics, pred_unet, pred_deeplab, X_val, y_val, indices


metrics, pred_unet, pred_deeplab, X_val, y_val, indices = load_data()

# ========================================
# 4. IMAGE NORMALIZATION
# ========================================
def normalize_for_display(img):
    img = img.copy()
    img = (img - img.min()) / (img.max() - img.min() + 1e-8)
    return np.clip(img, 0, 1)

# ========================================
# 5. HELPERS
# ========================================
def get_flood_label(mask, threshold=0.05):
    return "FLOOD" if np.mean(mask) >= threshold else "NO FLOOD"

def dice_score(gt, pred):
    return 2 * np.sum(gt * pred) / (np.sum(gt) + np.sum(pred) + 1e-7)

def plot_plotly_cm(cm, title, color_scale):
    labels = ["No Flood", "Flood"]
    cm_text = [[str(y) for y in x] for x in cm]
    fig = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            text=cm_text,
            texttemplate="%{text}",
            colorscale=color_scale,
            showscale=False,
            xgap=2,
            ygap=2,
        )
    )
    fig.update_layout(
        title={"text": title, "x": 0.5},
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
        height=450,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def img_card(col, img, title):
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.image(img, use_container_width=True)

# ========================================
# 6. SIDEBAR (CLEAN + DASHBOARD STYLE)
# ========================================
with st.sidebar:
    st.title("🌊 Flood AI Dashboard")
    st.markdown("Comparison of U-Net and DeepLabV3+ for flood segmentation.")
    st.markdown("---")

    st.subheader("Overall Performance")
    st.metric("U-Net Dice", f"{metrics['unet']['dice']:.4f}")
    st.metric("DeepLabV3+ Dice", f"{metrics['deeplab']['dice']:.4f}")

    winner = "DeepLabV3+" if metrics["deeplab"]["dice"] > metrics["unet"]["dice"] else "U-Net"
    st.success(f"**Winner: {winner}**")

    st.markdown("---")
    st.markdown("### Summary Table")
    summary_df = pd.DataFrame(
        {
            "Model": ["U-Net", "DeepLabV3+"],
            "Dice": [metrics["unet"]["dice"], metrics["deeplab"]["dice"]],
            "IoU": [metrics["unet"]["iou"], metrics["deeplab"]["iou"]],
            "Accuracy": [metrics["unet"]["accuracy"], metrics["deeplab"]["accuracy"]],
        }
    ).set_index("Model")
    st.dataframe(summary_df, use_container_width=True)

# ========================================
# 7. HEADER
# ========================================
st.title("U-Net vs DeepLabV3+ Flood Segmentation")
st.subheader("Interactive comparison of two state-of-the-art models on SAR flood detection")

# ========================================
# 8. TABS
# ========================================
tab_metrics, tab_preds, tab_cm = st.tabs(
    ["📊 Overall Metrics", "🖼️ Image Predictions", "🧮 Confusion Matrices"]
)

# ========================================
# TAB 1: METRICS
# ========================================
with tab_metrics:
    st.header("Performance Comparison")

    k1, k2, k3, k4 = st.columns(4, gap="large")
    with k1:
        st.metric("U-Net Dice", f"{metrics['unet']['dice']:.4f}")
    with k2:
        st.metric("U-Net IoU", f"{metrics['unet']['iou']:.4f}")
    with k3:
        st.metric("DeepLab Dice", f"{metrics['deeplab']['dice']:.4f}")
    with k4:
        st.metric("DeepLab IoU", f"{metrics['deeplab']['iou']:.4f}")

    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("U-Net")
            c1, c2, c3 = st.columns(3)
            c1.metric("Dice Score", f"{metrics['unet']['dice']:.4f}")
            c2.metric("IoU", f"{metrics['unet']['iou']:.4f}")
            c3.metric("Accuracy", f"{metrics['unet']['accuracy']:.4f}")
    with col2:
        with st.container(border=True):
            st.subheader("DeepLabV3+")
            c1, c2, c3 = st.columns(3)
            c1.metric("Dice Score", f"{metrics['deeplab']['dice']:.4f}")
            c2.metric("IoU", f"{metrics['deeplab']['iou']:.4f}")
            c3.metric("Accuracy", f"{metrics['deeplab']['accuracy']:.4f}")

    st.markdown("---")

    df = pd.DataFrame(
        {
            "Model": ["U-Net", "DeepLabV3+"],
            "Dice": [metrics["unet"]["dice"], metrics["deeplab"]["dice"]],
            "IoU": [metrics["unet"]["iou"], metrics["deeplab"]["iou"]],
            "Accuracy": [metrics["unet"]["accuracy"], metrics["deeplab"]["accuracy"]],
        }
    ).melt(id_vars="Model", var_name="Metric", value_name="Score")

    fig = px.bar(
        df,
        x="Metric",
        y="Score",
        color="Model",
        barmode="group",
        title="Model Performance by Metric",
        color_discrete_map={"U-Net": "#42A5F5", "DeepLabV3+": "#FF7043"},
        height=500,
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 2: PREDICTIONS (UI UPGRADE)
# ========================================
with tab_preds:
    st.header("Sample Prediction Visualization")

    with st.container(border=True):
        st.subheader("Choose a sample")
        c1, c2 = st.columns([2, 2], gap="large")
        with c1:
            sample_idx = st.slider("Sample Index", 0, len(indices) - 1, 0)
        with c2:
            threshold = st.slider("Flood Threshold", 0.0, 0.5, 0.05, 0.01)

    vv = X_val[sample_idx, :, :, 0]
    vh = X_val[sample_idx, :, :, 1]
    gt = y_val[sample_idx, :, :, 0]
    unet_pred = pred_unet[sample_idx, :, :, 0]
    deeplab_pred = pred_deeplab[sample_idx, :, :, 0]

    dice_unet = dice_score(gt, unet_pred)
    dice_deeplab = dice_score(gt, deeplab_pred)

    st.markdown("---")

    cols = st.columns(5, gap="large")
    img_card(cols[0], normalize_for_display(vv), "Input: VV Band")
    img_card(cols[1], normalize_for_display(vh), "Input: VH Band")
    img_card(cols[2], gt, f"Ground Truth • {get_flood_label(gt, threshold)}")
    img_card(cols[3], unet_pred, f"U-Net • {get_flood_label(unet_pred, threshold)} • Dice: {dice_unet:.3f}")
    img_card(cols[4], deeplab_pred, f"DeepLabV3+ • {get_flood_label(deeplab_pred, threshold)} • Dice: {dice_deeplab:.3f}")

# ========================================
# TAB 3: CONFUSION MATRIX (WITH EXTRA INSIGHTS)
# ========================================
with tab_cm:
    st.header("Pixel-Level Confusion Matrix")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            cm_unet = confusion_matrix(y_val.flatten(), pred_unet.flatten())
            fig_unet = plot_plotly_cm(cm_unet, "U-Net Confusion Matrix", "Blues")
            st.plotly_chart(fig_unet, use_container_width=True)

            cm = cm_unet.astype(float)
            acc = (cm.trace() / (cm.sum() + 1e-9))
            cm_norm = cm / (cm.sum(axis=1, keepdims=True) + 1e-9)
            st.caption(f"Overall pixel accuracy: {acc:.3f}")
            st.caption(f"Row-normalized: TN={cm_norm[0,0]:.3f}, FP={cm_norm[0,1]:.3f}, FN={cm_norm[1,0]:.3f}, TP={cm_norm[1,1]:.3f}")

    with col2:
        with st.container(border=True):
            cm_deeplab = confusion_matrix(y_val.flatten(), pred_deeplab.flatten())
            fig_deeplab = plot_plotly_cm(cm_deeplab, "DeepLabV3+ Confusion Matrix", "Oranges")
            st.plotly_chart(fig_deeplab, use_container_width=True)

            cm = cm_deeplab.astype(float)
            acc = (cm.trace() / (cm.sum() + 1e-9))
            cm_norm = cm / (cm.sum(axis=1, keepdims=True) + 1e-9)
            st.caption(f"Overall pixel accuracy: {acc:.3f}")
            st.caption(f"Row-normalized: TN={cm_norm[0,0]:.3f}, FP={cm_norm[0,1]:.3f}, FN={cm_norm[1,0]:.3f}, TP={cm_norm[1,1]:.3f}")

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.caption("Built with Streamlit • Models: U-Net & DeepLabV3+ • Data: SAR Flood Tiles")
