#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QHBoxLayout>
#include <QStyle>
#include <QProcess>
#include <QMessageBox>
#include <QFile>

QPushButton *storeButton;
QPushButton *gamesButton;
QPushButton *formsButton;
QPushButton *game1;
QPushButton *game2;
QPushButton *buy1;
QPushButton *buy2;
QString buttonMenuStyle;
QString selectedButtonMenuStyle;

class LauncherWidget : public QWidget {
Q_OBJECT

public:
    ~LauncherWidget() override = default;

public slots:
    void launchApplication();
};

void LauncherWidget::launchApplication() {
    QString program = "/Users/delamonicavictor/CLionProjects/untitled/games/memo";
    QStringList arguments;

    if (!QFile::exists(program)) {
        QMessageBox::critical(this, "Error", "Application not found at: " + program);
        return;
    }

    bool started = QProcess::startDetached(program, arguments);
    if (!started) {
        QMessageBox::critical(this, "Error", "Failed to launch application");
    }
}

void onStoreButtonClicked(QPushButton *buttonClicked) {
    if (buttonClicked == storeButton) {
        storeButton->setStyleSheet(selectedButtonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->show();
        buy2->show();
    } else if (buttonClicked == gamesButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(selectedButtonMenuStyle);
        formsButton->setStyleSheet(buttonMenuStyle);
        game1->show();
        game2->show();
        buy1->hide();
        buy2->hide();
    } else if (buttonClicked == formsButton) {
        storeButton->setStyleSheet(buttonMenuStyle);
        gamesButton->setStyleSheet(buttonMenuStyle);
        formsButton->setStyleSheet(selectedButtonMenuStyle);
        game1->hide();
        game2->hide();
        buy1->hide();
        buy2->hide();
    }
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);


    storeButton = new QPushButton("Store");
    gamesButton = new QPushButton("Games");
    formsButton = new QPushButton("Forms");

    buttonMenuStyle = "QPushButton { "
                           "border-top-left-radius: 20px; "
                           "border-bottom-left-radius: 24px; "
                           "padding: 5px; "
                           "opacity: 50%; "
                           "background-color: #3C3C3C; "
                           //a "background-color: #6A6A6A; "
                           "}";
    selectedButtonMenuStyle = "QPushButton { "
                                   "border-top-left-radius: 20px; "
                                   "border-bottom-left-radius: 24px; "
                                   "padding: 5px; "
                                   "opacity: 50%; "
                                   "background-color: #6A6A6A; "
                                   "}";

    LauncherWidget window;
    window.setWindowTitle("Thera Duty");
    window.setStyleSheet("background-color: #3C3C3C;");

    storeButton->setFixedHeight(100);
    storeButton->setStyleSheet(selectedButtonMenuStyle);
    storeButton->setCursor(Qt::PointingHandCursor);
    QObject::connect(storeButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(storeButton);
    });

    gamesButton->setFixedHeight(100);
    gamesButton->setStyleSheet(buttonMenuStyle);
    gamesButton->setCursor(Qt::PointingHandCursor);
    QObject::connect(gamesButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(gamesButton);
    });

    formsButton->setFixedHeight(100);
    formsButton->setStyleSheet(buttonMenuStyle);
    formsButton->setCursor(Qt::PointingHandCursor);
    QObject::connect(formsButton, &QPushButton::clicked, []() {
        onStoreButtonClicked(formsButton);
    });

    auto mainRow = new QHBoxLayout;
    auto layout = new QVBoxLayout;
    layout->addWidget(storeButton);
    layout->addWidget(gamesButton);
    layout->addWidget(formsButton);

    auto *storeColumn = new QVBoxLayout;
    storeColumn->setAlignment(Qt::AlignTop);
    auto demoGame = new QHBoxLayout;
    game1 = new QPushButton("Memo");
    QObject::connect(game1, &QPushButton::clicked, &window, &LauncherWidget::launchApplication);
    game2 = new QPushButton("Game 2");
    buy1 = new QPushButton("Buy Game 3");
    buy2 = new QPushButton("Buy Game 4");
    demoGame->addWidget(game1);
    demoGame->addWidget(game2);
    demoGame->addWidget(buy1);
    demoGame->addWidget(buy2);
    game1->hide();
    game2->hide();
    storeColumn->addLayout(demoGame);
    mainRow->addLayout(layout);
    mainRow->addLayout(storeColumn);


    window.setLayout(mainRow);

    window.resize(800, 600);
    window.show();

    return QApplication::exec();
}

#include "main.moc"