## Bai 01

# (a)
Finv = function (q){ q ^ (1/3) }
U = runif(100, min = 0, max = 1)
res = Finv(U)
print(res)

# (b)
Finv = function (q){ exp(q / log(3/2)) }
U = runif(100, min = (log(3) - log(2)) * log(2), max = (log(3) - log(2)) * log(3))
res = Finv(U)
print(res)

# (c)
Finv = function (q){ acos(-2 * q) } 
U = runif(100, min = -1/2, max = 1/2)
res = Finv(U)
print(res)





	
## Bai 02
#__________
sampleMean = function(generator, nSimulation, sampleSize){
    # generator: Ham phat sinh cac so ngau nhien
    # nSimulation: So lan mo phong
    # sampleSize: Co mau
    Xmean  = rep(0, nSimulation)
    for(i in 1:nSimulation){
        Xmean[i] = mean(generator(sampleSize))
    }
    return(Xmean)
}
## VD: (X1, X2, ..., Xn) ~ U[0, 1]
nSimulation = 10^5
n = 100
generator = function(n){ runif(n, min = 0, max = 1) }
Xmean = sampleMean(generator, nSimulation, n)
mu = 1/2
sigmasq = 1/12
hist(Xmean, breaks = 100, freq = FALSE)
curve(dnorm(x, mean = mu, sd = sqrt(sigmasq/n)), add = TRUE, col = 'red', lwd = 2)
#___________
# (a)
sampleMean = function(generator, nSimulation, sampleSize){
    # generator: Ham phat sinh cac so ngau nhien
    # nSimulation: So lan mo phong
    # sampleSize: Co mau
    Xmean  = rep(0, nSimulation)
    for(i in 1:nSimulation){
        Xmean[i] = mean(generator(sampleSize))
    }
    return(Xmean)
}
nS = 10^5
n = 500
g = function(n) { runif(n, min = -sqrt(3), max = sqrt(3)) }
Xmean = sampleMean(g, nS, n)
hist(Xmean, breaks = 500, freq = FALSE)
mu = 0
sigma = 1
curve(dnorm(x, mu, sqrt(sigma/n)), add = TRUE, col = 'red', lwd = 2)


# (b)
sampleMean = function(generator, nSimulation, sampleSize){
    # generator: Ham phat sinh cac so ngau nhien
    # nSimulation: So lan mo phong
    # sampleSize: Co mau
    Xmean  = rep(0, nSimulation)
    for(i in 1:nSimulation){
        Xmean[i] = mean(generator(sampleSize))
    }
    return(Xmean)
}
nS = 10^5
n = 1000
g = function(n) { runif(n, min = 0, max = 10) }
Xmean = sampleMean(g, nS, n)
hist(Xmean, breaks = 1000, freq = FALSE)
mu = 5
sigma = 25/3
curve(dnorm(x, mu, sqrt(sigma/n)), add = TRUE, col = 'red', lwd = 2)

# (c)
set.seed(123)
sampleMean = function(generator, nSimulation, sampleSize){
    # generator: Ham phat sinh cac so ngau nhien
    # nSimulation: So lan mo phong
    # sampleSize: Co mau
    Xmean  = rep(0, nSimulation)
    for(i in 1:nSimulation){
        Xmean[i] = mean(generator(sampleSize))
    }
    return(Xmean)
}

nS = 10^5
n = 1000

generate = function(n) {
    Finv = function (q){ q ^ (1 / 3) }
    U = runif(n, min = 0, max = 1)
    res = Finv(U)
    return (res)
}

Xmean = sampleMean(generate, nS, n)  # Truyền hàm generate thay vì kết quả của nó
hist(Xmean, breaks = 1000, freq = FALSE)
mu = 3/4
sigma = 3/80
curve(dnorm(x, mu, sqrt(sigma/n)), add = TRUE, col = 'red', lwd = 2)


# (d)
sampleMean = function(generator, nSimulation, sampleSize){
    # generator: Ham phat sinh cac so ngau nhien
    # nSimulation: So lan mo phong
    # sampleSize: Co mau
    Xmean  = rep(0, nSimulation)
    for(i in 1:nSimulation){
        Xmean[i] = mean(generator(sampleSize))
    }
    return(Xmean)
}

nS = 10^5
n = 1000

generate = function(n) {
    Finv = function (q){ exp(q / log(3/2)) }
    U = runif(n, min = (log(3) - log(2)) * log(2), max = (log(3) - log(2)) * log(3))
    res = Finv(U)
    return (res)
}

Xmean = sampleMean(generate, nS, n)  # Truyền hàm generate thay vì kết quả của nó
hist(Xmean, breaks = 1000, freq = FALSE)



























# Các tham số
n_values <- 10:200  # Giá trị n từ 10 đến 200
p <- 2/3            # Xác suất thành công
size <- 2 * n_values  # Số lần thử (2n)

# (a) Tính ln(P(X <= n)) với X ~ B(2n, 2/3)
ln_P <- sapply(n_values, function(n) {
  log(pbinom(n, size = 2 * n, prob = p))  # P(X <= n)
})

# (b) Tính ln(Phi(...)) (không hiệu chỉnh liên tục)
ln_Phi <- sapply(n_values, function(n) {
  z <- (n - 2 * n * p) / sqrt(4 * n * p * (1 - p))
  log(pnorm(z))
})

# (c) Tính ln(Phi(...)) (có hiệu chỉnh liên tục)
ln_Phi_adjusted <- sapply(n_values, function(n) {
  z <- (n + 0.5 - 2 * n * p) / sqrt(4 * n * p * (1 - p))
  log(pnorm(z))
})

# Vẽ đồ thị
plot(n_values, ln_P, type = "l", col = "black", lwd = 2,
     xlab = "n", ylab = "ln(P)", main = "Hiệu chỉnh liên tục")
lines(n_values, ln_Phi, col = "red", lwd = 2)       # Đường không hiệu chỉnh
lines(n_values, ln_Phi_adjusted, col = "blue", lwd = 2)  # Đường hiệu chỉnh
legend("bottomright", legend = c("ln(P(X <= n))", "ln(Phi(...))", "ln(Phi(...)) - Hiệu chỉnh"),
       col = c("black", "red", "blue"), lwd = 2)



