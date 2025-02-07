from flask import Blueprint, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from celery import shared_task
import uuid
import os
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_pipeline import LivePortraitPipeline

UPLOAD_FOLDER = "/app/uploads"
OUTPUT_FOLDER = "/app/outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# Load model configuration
inference_cfg = InferenceConfig()
crop_cfg = CropConfig()
pipeline = LivePortraitPipeline(inference_cfg, crop_cfg)

main = Blueprint('main', __name__, template_folder='templates')

@shared_task(ignore_result=False, bind=True)
def run_pipeline(self, **kwargs):
    """Celery task to run the animation pipeline with user-defined arguments."""
    try:
        # Ensure required arguments are provided
        if 'source' not in kwargs or 'driving' not in kwargs:
            raise ValueError("Both 'source' and 'driving' are required arguments.")

        args_user = {
            'source': kwargs['source'],
            'driving': kwargs['driving'],
            'flag_normalize_lip': kwargs.get('flag_normalize_lip', False),
            'flag_relative_motion': kwargs.get('flag_relative_input', True),
            'flag_do_crop': kwargs.get('flag_do_crop_input', True),
            'flag_pasteback': kwargs.get('flag_remap_input', True),
            'flag_stitching': kwargs.get('flag_stitching_input', True),
            'animation_region': kwargs.get('animation_region', 'all'),
            'driving_option': kwargs.get('driving_option_input', 'expression-friendly'),
            'driving_multiplier': kwargs.get('driving_multiplier', 1.0),
            'flag_crop_driving_video': kwargs.get('flag_crop_driving_video_input', False),
            'scale': kwargs.get('scale', 2.3),
            'vx_ratio': kwargs.get('vx_ratio', 0),
            'vy_ratio': kwargs.get('vy_ratio', -0.125),
            'scale_crop_driving_video': kwargs.get('scale_crop_driving_video', 2.2),
            'vx_ratio_crop_driving_video': kwargs.get('vx_ratio_crop_driving_video', 0.0),
            'vy_ratio_crop_driving_video': kwargs.get('vy_ratio_crop_driving_video', -0.1),
            'driving_smooth_observation_variance': kwargs.get('driving_smooth_observation_variance', 3e-7),
        }

        # Convert mapped arguments to ArgumentConfig
        args = ArgumentConfig(
            source=args_user['source'],
            driving=args_user['driving'],
            flag_normalize_lip=args_user['flag_normalize_lip'],
            flag_relative_motion=args_user['flag_relative_motion'],
            flag_do_crop=args_user['flag_do_crop'],
            flag_pasteback=args_user['flag_pasteback'],
            flag_stitching=args_user['flag_stitching'],
            animation_region=args_user['animation_region'],
            driving_option=args_user['driving_option'],
            driving_multiplier=args_user['driving_multiplier'],
            flag_crop_driving_video=args_user['flag_crop_driving_video'],
            scale=args_user['scale'],
            vx_ratio=args_user['vx_ratio'],
            vy_ratio=args_user['vy_ratio'],
            scale_crop_driving_video=args_user['scale_crop_driving_video'],
            vx_ratio_crop_driving_video=args_user['vx_ratio_crop_driving_video'],
            vy_ratio_crop_driving_video=args_user['vy_ratio_crop_driving_video'],
            driving_smooth_observation_variance=args_user['driving_smooth_observation_variance'],
            output_dir=OUTPUT_FOLDER
        )

        # Execute pipeline
        output_file, _ = pipeline.execute(args)  # Run the inference

        return {"output_file": output_file}

    except Exception as e:
        return {"error": str(e)}




@main.route("/predict", methods=["POST"])
def predict():
    """Handle image/video animation inference."""
    if "source" not in request.files or "driving" not in request.files:
        return jsonify({"error": "Please upload both source and driving files"}), 400

    # Save source and driving files
    source_file = request.files["source"]
    driving_file = request.files["driving"]

    source_filename = secure_filename(source_file.filename)
    driving_filename = secure_filename(driving_file.filename)

    source_path = os.path.join(UPLOAD_FOLDER, f"source_{uuid.uuid4().hex}_{source_filename}")
    driving_path = os.path.join(UPLOAD_FOLDER, f"driving_{uuid.uuid4().hex}_{driving_filename}")

    source_file.save(source_path)
    driving_file.save(driving_path)

    # Collect additional arguments from request
    additional_args = request.form.to_dict()
    additional_args = {key: (val if val.lower() not in ['true', 'false'] else val.lower() == 'true') for key, val in additional_args.items()}

    # Send task to Celery with all parameters
    task = run_pipeline.delay(source=source_path, driving=driving_path, **additional_args)

    # Return the task ID to check the status later
    return jsonify({"task_id": task.id, "status_url": url_for("main.task_status", task_id=task.id, _external=True)})


@main.route("/task_status/<task_id>", methods=["GET"])
def task_status(task_id):
    """Check the status of a Celery task."""
    task = run_pipeline.AsyncResult(task_id)

    if task.state == "PENDING":
        response = {"status": "PENDING"}
    elif task.state == "FAILURE":
        response = {"status": "FAILED", "error": str(task.info)}
    elif task.state == "SUCCESS":
        response = {"status": "COMPLETED", "output_file": url_for("main.download_output", filename=os.path.basename(task.result["output_file"]), _external=True)}
    else:
        response = {"status": task.state}

    return jsonify(response)


@main.route("/download/<filename>", methods=["GET"])
def download_output(filename):
    """Download the generated output file."""
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404
