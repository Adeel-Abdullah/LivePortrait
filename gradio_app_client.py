from gradio_client import Client, handle_file

client = Client("https://b5c7634626875add18.gradio.live/", auth=("Adeel_Abdullah", "LivePortraitApp"))

client.predict(
  example_tuple=0,
  api_name="/load_example_2"
)

client.predict(
  param_0=handle_file('file.jpg'),
  param_1=None,
  param_2={"video":handle_file('d0.mp4'),"subtitles":None},
  param_3=None,
  param_4=None,
  param_5=False,
  param_6=True,
  param_7=True,
  param_8=True,
  param_9=True,
  param_10="all",
  param_11="expression-friendly",
  param_12=1,
  param_13=False,
  param_14=2.3,
  param_15=0,
  param_16=-0.125,
  param_17=2.2,
  param_18=0,
  param_19=-0.1,
  param_20=3e-7,
  param_21="",
  param_22="",
  api_name="/gpu_wrapped_execute_video"
)
