library(shiny)
library(e1071)

# Define UI
ui <- fluidPage(
  titlePanel("Normal Distribution Tinkerer"),
  sidebarLayout(
    sidebarPanel(
      numericInput("mean", "Mean", 0, min = -100, max = 100),
      numericInput("sd", "Standard Deviation", 1, min = 0.1, max = 100),
      sliderInput("n", "Sample Size", min = 100, max = 10000, value = 100, step = 10),
      sliderInput("skew", "Skewness", min = -15, max = 15, value = 0, step = 0.1),
      br(),
      actionButton("randomize", "Randomize"),
      actionButton("reset", "Reset")
    ),
    mainPanel(
      plotOutput("distplot"),
      br(),
      h4("Mean:"),
      verbatimTextOutput("meanout"),
      h4("Median:"),
      verbatimTextOutput("medianout")
    )
  )
)

# Define server
server <- function(input, output, session) {
  # Generate initial data
  data <- reactive({
    rnorm(input$n, input$mean, input$sd) + input$skew * abs(rnorm(input$n, 0, 1))
  })
  
  # Generate plot
  output$distplot <- renderPlot({
    hist(data(), main = "Normal Distribution", xlab = "Value", ylab = "Frequency", col = "gray", breaks = sqrt(input$n))
    abline(v = mean(data()), col = "red", lwd = 2)
    abline(v = median(data()), col = "blue", lwd = 2)
    legend("topright", legend = c("Mean", "Median"), col = c("red", "blue"), lwd = 2)
  })
  
  # Calculate mean
  output$meanout <- renderPrint({
    mean(data())
  })
  
  # Calculate median
  output$medianout <- renderPrint({
    median(data())
  })
  
  # Randomize data
  observeEvent(input$randomize, {
    data(rnorm(input$n, input$mean, input$sd) + input$skew * abs(rnorm(input$n, 0, 1)))
  })
  
  # Reset data
  observeEvent(input$reset, {
    data(rnorm(input$n, 0, 1))
  })
}

# Run app
shinyApp(ui, server)

