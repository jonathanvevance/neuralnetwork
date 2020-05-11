import numpy as np

def SGD(network, X_train, Y_train, lossfunction,
        learning_rate, regularizer, accelerator):

    prev_loss = 0
    while True:
        permut = np.random.permutation(len(Y_train))
        X_train = X_train[permut]
        Y_train = Y_train[permut]
        for idx, x in enumerate(X_train):

            network.clear_outputs()
            ypred = network.forward(x)
            op_gradient = lossfunction.gradient(ypred, Y_train[idx, None])
            network.backward(op_gradient, regularizer) # gradients are available

            if accelerator != None:
                update = accelerator(learning_rate, network.Wgrad)
                network.W += update

            else:
                network.W -= learning_rate * network.Wgrad # SGD update

        total_loss = 0
        network.clear_outputs()
        for idx, x in enumerate(X_train):
            ypred = network.forward(x)
            total_loss += lossfunction.calc_loss(ypred, Y_train[idx, None])
        total_loss += regularizer.calc_loss(network.W)

        if abs(prev_loss - total_loss) < 0.01:
            break # stopping condition

        elif total_loss > 3 * prev_loss:
            print('Exploding cost')
            break

        prev_loss = total_loss

def MiniBatchGD(network, X_train, Y_train, lossfunction, batch_size,
                learning_rate, regularizer, accelerator):

    prev_loss = 0
    while True:
        permut = np.random.permutation(len(Y_train))
        X_train = X_train[permut]
        Y_train = Y_train[permut]

        for batch_num in range(len(Y_train) // batch_size):
            start_idx = batch_num * batch_size
            end_idx = min(len(Y_train), batch_num * batch_size + batch_size)
            Wgrad = np.zeros(np.shape(network.Wgrad))
            for idx in range(start_idx, end_idx):

                network.clear_outputs()
                ypred = network.forward(X_train[idx, None])
                op_gradient = lossfunction.gradient(ypred, Y_train[idx, None])
                network.backward(op_gradient)
                Wgrad += network.Wgrad # assuming lossfunction is a total sum

            if accelerator != None:
                update = accelerator(learning_rate, Wgrad)
                network.W += update

            else:
                network.W -= learning_rate * Wgrad

        total_loss = 0
        network.clear_outputs()
        for idx, x in enumerate(X_train):
            ypred = network.forward(x)
            total_loss += lossfunction.calc_loss(ypred, Y_train[idx, None])
        total_loss += regularizer.calc_loss(network.W)

        if abs(prev_loss - total_loss) < 0.01:
            break # stopping condition

        elif total_loss > 3 * prev_loss:
            print('Exploding cost')
            break

        prev_loss = total_loss

