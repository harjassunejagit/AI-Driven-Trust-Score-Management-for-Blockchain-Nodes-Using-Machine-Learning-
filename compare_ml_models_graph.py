import matplotlib.pyplot as plt

# Model names and accuracies
models = ['Logistic Regression', 'SVM', 'Random Forest']
accuracies = [0.7781, 0.7834, 0.9590]

# Plot
plt.figure()
plt.bar(models, accuracies)
plt.xlabel('Machine Learning Models')
plt.ylabel('Accuracy')
plt.title('Accuracy Comparison of Machine Learning Models')

# Save graph
plt.savefig('model_accuracy_comparison.png')

# Show graph
plt.show()
