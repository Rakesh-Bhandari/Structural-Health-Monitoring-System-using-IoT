import os
import base64
import json
from inference_sdk import InferenceHTTPClient

# Initialize Roboflow client
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="cm89aQXKE5csMXuUBcm3"
)

WORKSPACE_NAME = "mini-project-alaox"
WORKFLOW_ID = "detect-count-and-visualize"

# Paths
input_folder = "input_images"
output_folder = "output_images"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_folder, filename)
        print(f"\nProcessing {filename}...")

        try:
            result_list = client.run_workflow(
                workspace_name=WORKSPACE_NAME,
                workflow_id=WORKFLOW_ID,
                images={"image": input_path},
                use_cache=True
            )

            # Parse the result properly
            result_json_str = json.dumps(result_list)
            result_data = json.loads(result_json_str)

            if isinstance(result_data, list) and len(result_data) > 0:
                result = result_data[0]

                # ✅ Extract fields
                count_objects_b64 = result.get('count_objects')
                output_image_b64 = result.get('output_image')
                predictions = result.get('predictions')

                print(f"Predictions (object count): {predictions}")

                # Decode and save count_objects image
                if count_objects_b64:
                    image_data = base64.b64decode(count_objects_b64)
                    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_count.jpg")
                    with open(output_path, 'wb') as f_out:
                        f_out.write(image_data)
                    print(f"Saved count_objects image to {output_path}")
                else:
                    print("No count_objects image data found.")

                # Decode and save output_image
                if output_image_b64:
                    image_data = base64.b64decode(output_image_b64)
                    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_output.jpg")
                    with open(output_path, 'wb') as f_out:
                        f_out.write(image_data)
                    print(f"Saved output_image image to {output_path}")
                else:
                    print("No output_image image data found.")

            else:
                print("No results returned by the API.")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("\nAll images processed.")
