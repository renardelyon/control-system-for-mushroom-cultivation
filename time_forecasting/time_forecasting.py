import os
import datetime

import numpy as np
import pandas as pd
import tensorflow as tf

class Data:
	def __init__(self, data, features):
		self.features = features
		self.df = pd.DataFrame(data=data, columns=features)
		self.train_df = pd.DataFrame(columns=features)
		self.test_df = pd.DataFrame(columns=features)
		self.test_df_ori = pd.DataFrame(columns=features)
  
	def split(self):
		# length of df
		n = len(self.df)

		#split train and test data
		self.train_df = self.df[0:int(n*0.8)]
		self.test_df = self.df[int(n*0.8):]

		#make a copy of test_df
		self.test_df_ori = self.test_df.copy()
		return self
  
	def normalization(self):
		'''perform standardization'''
		train_mean = self.train_df.mean()
		test_mean = self.test_df.mean()
		train_std = self.train_df.std()
		test_std = self.test_df.std()
		
		self.train_df.loc[:, self.features] -= train_mean
		self.train_df.loc[:, self.features] /= train_std
                                            
		self.test_df.loc[:, self.features] -= test_mean
		self.test_df.loc[:, self.features] /= test_std
                                                                                                         
		return 'Data is normalized'
  
	def denormalization(self, x):
		""" x is data that wanted to be denormalize"""
		mean = self.test_df_ori.mean()[self.features[0]]
		std = self.test_df_ori.std()[self.features[0]]
		x = x * std + mean
		x = x.astype('int32')
		x = np.squeeze(x)
    
		return x
    
class WindowGenerator:
	def __init__(self, input_width, label_width, shift, 
					train_df, label_columns=None):
		self.train_df = train_df

		self.label_columns = label_columns
		if label_columns is not None:
			self.label_columns_indices = {name: i for i, name in 
                                    enumerate(label_columns)}
		self.columns_indices = {name: i for i, name in 
                           enumerate(train_df.columns)}
		self.input_width = input_width
		self.label_width = label_width
		self.shift = shift

		self.total_windows_size = input_width + shift
    
		self.input_indices = np.arange(self.total_windows_size)[:self.input_width]

		self.label_start = self.total_windows_size - self.label_width
		self.label_indices = np.arange(self.total_windows_size)[self.label_start:]

		self.data = []

	def split_window(self, features):
		inputs = features[:, :self.input_width, :]
		labels = features[:, self.label_start:, :]
		if self.label_columns is not None:
			labels = tf.stack([labels[:, :, self.columns_indices[name]] 
                         for name in self.label_columns], axis=-1)
    
		inputs.set_shape([None, self.input_width, None])
		labels.set_shape([None, self.label_width, None])

		return inputs, labels
  
	def make_dataset(self, data):
		data = np.array(data, dtype=np.float32)
		ds = tf.keras.preprocessing.timeseries_dataset_from_array(
				data=data,
				targets=None,
				sequence_length=self.total_windows_size,
				sequence_stride=1,
				shuffle=True,
				batch_size=32,)

		ds = ds.map(self.split_window)

		return ds
  
	@property
	def train(self):
		return self.make_dataset(self.train_df)

	@property
	def example(self):
		"""Get and cache an example batch of `inputs, labels` for plotting."""
		result = getattr(self, '_example', None)
		if result is None:
			# No example batch was found, so get one from the `.train` dataset
			result = next(iter(self.train))
			# And cache it for next time
			self._example = result
		return result  
  
	def __repr__(self):
		return '\n'.join([
			'Total window size: {}'.format(self.total_windows_size),
			'Input indices: {}'.format(self.input_indices),
			'Label indices: {}'.format(self.label_indices),
			'Label column name(s): {}'.format(self.label_columns)])
			
class TrainPredict:
	def __init__(self, window, EPOCHS=15):
		self.model = None
		self.EPOCHS = EPOCHS
		self.window = window

	def build_model(self, OUT_STEPS, num_features):
		self.model = tf.keras.Sequential([
		# Shape [batch, time, features] => [batch, lstm_units]
		# Adding more `lstm_units` just overfits more quickly.
		tf.keras.layers.LSTM(32, return_sequences=False),
		# Shape => [batch, out_steps*features]
		tf.keras.layers.Dense(OUT_STEPS*num_features,
                          kernel_initializer=tf.initializers.zeros()),
		# Shape => [batch, out_steps, features]
		tf.keras.layers.Reshape([OUT_STEPS, num_features])])

		return self


	def compile_and_fit(self, patience=4):
		early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss',
                                                    patience=patience,
                                                    mode='min')

		self.model.compile(loss=tf.losses.MeanSquaredError(),
                optimizer=tf.optimizers.Adam(),
                metrics=[tf.metrics.MeanAbsoluteError()])

		history = self.model.fit(self.window.train, epochs=self.EPOCHS)
		return history
  
	def inference(self, X):
		pred = self.model.predict(X)
		return pred

if __name__=="__main__":
	df = pd.read_csv('/home/pi/TA_lyon/latihan/data/data.csv')
	df['Time'] /=3600
	df = df.dropna()
	df.drop(columns='Date', inplace=True)
	test_data = df[['Humidity (%)', 'Temp (C)']].to_numpy()
	data = Data(test_data, ['Humidity', 'Temp'])
	data.split().normalization()
	print(data.train_df)
	OUT_STEPS =  20
	wide_window = WindowGenerator(
		train_df=data.train_df,
		input_width=100, label_width=OUT_STEPS, shift=OUT_STEPS,
		label_columns=['Humidity'])

	train_predict = TrainPredict(wide_window)
	tf.keras.backend.clear_session()
	num_features = data.train_df.shape[-1]
	train_predict.build_model(OUT_STEPS, num_features).compile_and_fit()

