use std::collections::HashSet;
use chrono::prelude::*;

#[derive(Debug,Hash,Eq,PartialEq)]
struct Project {
    name: String,
    date: NaiveDate,
}

impl Project {
    fn from(name: &str, date: NaiveDate) -> Self {
        Self {
            name: name.to_string(),
            date,
        }
    }
    fn print_markdown(&self) {
        println!("{} - {}", self.name, self.date);
    }
}

#[derive(Debug)]
struct Discography {
    artist_name: String,
    projects: HashSet<Project>,
}

impl Discography {
    fn from(artist_name: &str) -> Self {
        Self {
            artist_name: artist_name.to_string(), 
            projects: HashSet::new(),
        }
    }
    fn print_markdown(&self) {
        println!("# {}", self.artist_name);
        for project in self.get_sorted_projects() {
            println!();
            project.print_markdown();
        }
        println!();
    }
    fn get_sorted_projects(&self) -> Vec<&Project> {
        let mut projects: Vec<_> = self.projects.iter().collect();
        projects.sort_by_key(|p| p.date);
        projects
    }
}

fn main() {
    let mut discography = Discography::from("Atlas");
    discography.projects.insert(Project::from("Skeletons", NaiveDate::from_ymd_opt(2017, 12, 8).unwrap()));
    discography.projects.insert(Project::from("Autumn", NaiveDate::from_ymd_opt(2016, 9, 8).unwrap()));
    discography.projects.insert(Project::from("Roses", NaiveDate::from_ymd_opt(2016, 7, 8).unwrap()));
    discography.projects.insert(Project::from("Windmills", NaiveDate::from_ymd_opt(2017, 11, 9).unwrap()));
    discography.print_markdown();
}
